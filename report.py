"""
report.py — WAF Attack Report & PDF Export  (Port 5003)
Routes:
  /              → live attack report dashboard
  /download/pdf  → download full report as PDF
"""

from flask import Flask, render_template_string, send_file
import json, os, io
from datetime import datetime
from collections import Counter

app = Flask(__name__)

LOG_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attacks.log')
BLOCKED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocked_ips.json')

# ── helpers ───────────────────────────────────────────────────────────────────
def classify(log):
    t = log.get('attack_type', '')
    if t: return t
    p = log.get('payload', '').lower()
    if any(x in p for x in [' or ', 'union select', 'drop table', 'insert into', 'sleep(', '--', '1=1']):
        return 'SQL Injection'
    if any(x in p for x in ['<script', 'javascript:', 'onerror=', 'onload=', 'iframe', 'alert(', 'eval(']):
        return 'XSS'
    if any(x in p for x in ['; ls', '; cat', '| whoami', '&&', 'cmd.exe']):
        return 'Command Injection'
    if any(x in p for x in ['../', 'etc/passwd', 'etc/shadow', '/var/']):
        return 'Path Traversal'
    return 'Unknown'

def load_logs():
    logs = []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    try: logs.append(json.loads(line))
                    except: pass
    except FileNotFoundError:
        pass
    return logs

def get_blocked_count():
    try:
        with open(BLOCKED_FILE) as f:
            return len(json.load(f).get('blocked_ips', []))
    except:
        return 0

def get_stats(logs):
    return Counter(classify(l) for l in logs), Counter(l.get('ip', 'unknown') for l in logs)

# ── HTML template ─────────────────────────────────────────────────────────────
MATRIX_JS = r"""
<script>
window.addEventListener('DOMContentLoaded', function() {
  var canvas = document.getElementById('matrix');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(){}[]<>/\|;:!?~`';
  var W, H, cols, drops;
  function init() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    cols = Math.floor(W / 16);
    drops = [];
    for (var i = 0; i < cols; i++) drops[i] = Math.random() * -50;
  }
  init();
  window.addEventListener('resize', init);
  setInterval(function() {
    ctx.fillStyle = 'rgba(5,10,5,0.05)';
    ctx.fillRect(0, 0, W, H);
    for (var i = 0; i < drops.length; i++) {
      var ch = chars[Math.floor(Math.random() * chars.length)];
      var x = i * 16;
      var y = drops[i] * 16;
      ctx.fillStyle = '#ccffcc';
      ctx.font = 'bold 13px monospace';
      ctx.fillText(ch, x, y);
      ctx.fillStyle = '#00ff41';
      ctx.font = '12px monospace';
      if (Math.random() > 0.5 && y > 16)
        ctx.fillText(chars[Math.floor(Math.random() * chars.length)], x, y - 16);
      if (y > H && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
  }, 45);
});
</script>
"""

REPORT_HTML = ("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Attack Report -- {{ total }} Detected</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root {
  --bg:#050a05; --bg2:#070d07; --bg3:#0a120a; --panel:#0c160c;
  --border:rgba(0,255,65,0.15); --border2:rgba(0,255,65,0.35);
  --g:#00ff41; --g2:#00cc33; --g3:#008f23;
  --dim:rgba(0,255,65,0.45); --muted:rgba(0,255,65,0.3);
  --red:#ff0040; --amber:#ffaa00; --cyan:#00ffff;
  --violet:#a855f7; --orange:#ff8800; --text:#c8ffc8;
}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{font-family:'Share Tech Mono',monospace;background:var(--bg);color:var(--g);min-height:100vh;overflow-x:hidden;}
#matrix{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.1;}
body::after{content:'';position:fixed;inset:0;z-index:999;pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.07) 2px,rgba(0,0,0,0.07) 4px);}
body::before{content:'';position:fixed;inset:0;z-index:998;pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.55) 100%);}

@keyframes glitch{0%,100%{text-shadow:none;transform:none;}20%{text-shadow:-2px 0 var(--red),2px 0 var(--cyan);transform:translate(-1px,0);}40%{text-shadow:2px 0 var(--red),-2px 0 var(--cyan);transform:translate(1px,0);}60%{text-shadow:none;transform:none;}80%{text-shadow:-1px 0 var(--cyan);transform:translate(1px,0);}}
@keyframes flicker{0%,100%{opacity:1}41%{opacity:1}42%{opacity:0.6}43%{opacity:1}75%{opacity:1}76%{opacity:0.7}77%{opacity:1}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
@keyframes scanH{0%{top:-4px}100%{top:100%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes bar-grow{from{width:0}to{width:var(--w)}}
@keyframes glow-pulse{0%,100%{box-shadow:0 0 8px rgba(0,255,65,0.25),inset 0 0 6px rgba(0,255,65,0.04)}50%{box-shadow:0 0 18px rgba(0,255,65,0.5),inset 0 0 12px rgba(0,255,65,0.08)}}

.scan-line{position:fixed;left:0;right:0;height:2px;z-index:997;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(0,255,65,0.35),transparent);animation:scanH 8s linear infinite;}

/* NAV */
nav{position:sticky;top:0;z-index:200;display:flex;justify-content:space-between;align-items:center;
  padding:14px 48px;background:rgba(5,10,5,0.93);backdrop-filter:blur(14px);
  border-bottom:1px solid var(--border);animation:flicker 10s infinite;}
.logo{font-family:'Orbitron',monospace;font-size:14px;font-weight:900;color:var(--g);letter-spacing:4px;
  text-shadow:0 0 20px var(--g),0 0 40px rgba(0,255,65,0.3);animation:glitch 7s infinite;}
.nav-left{display:flex;align-items:center;gap:20px;}
.live-badge{display:flex;align-items:center;gap:7px;font-size:9px;color:var(--dim);
  border:1px solid var(--border);padding:4px 12px;border-radius:2px;letter-spacing:2px;}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--amber);
  box-shadow:0 0 8px var(--amber);animation:blink 1s ease-in-out infinite;}
.nav-links{display:flex;gap:24px;align-items:center;}
.nav-links a{font-size:10px;color:var(--dim);text-decoration:none;letter-spacing:2px;transition:color 0.2s,text-shadow 0.2s;}
.nav-links a:hover{color:var(--g);text-shadow:0 0 8px var(--g);}
.nav-pdf-btn{font-size:10px;color:var(--amber);text-decoration:none;letter-spacing:2px;
  border:1px solid rgba(255,170,0,0.4);padding:5px 14px;border-radius:3px;transition:all 0.2s;
  text-shadow:0 0 8px rgba(255,170,0,0.4);box-shadow:0 0 10px rgba(255,170,0,0.1);}
.nav-pdf-btn:hover{background:rgba(255,170,0,0.08);box-shadow:0 0 20px rgba(255,170,0,0.3);color:var(--amber);}

/* MAIN */
main{position:relative;z-index:1;max-width:1380px;margin:0 auto;padding:44px 48px 60px;}

/* HEADER */
.page-head{margin-bottom:36px;opacity:0;animation:fadeUp 0.5s ease 0.1s forwards;}
.page-head h1{font-family:'Orbitron',monospace;font-size:30px;font-weight:900;letter-spacing:2px;
  text-shadow:0 0 24px rgba(0,255,65,0.4);margin-bottom:6px;}
.page-head h1 span{color:var(--amber);text-shadow:0 0 20px rgba(255,170,0,0.5);}
.page-head p{font-size:11px;color:var(--dim);letter-spacing:1px;}
.refresh-row{display:flex;align-items:center;gap:14px;margin-top:8px;}
.gen-time{font-size:10px;color:var(--g3);letter-spacing:2px;}
.countdown{font-size:10px;color:var(--amber);border:1px solid rgba(255,170,0,0.3);
  padding:3px 12px;border-radius:2px;letter-spacing:1px;}

/* STAT CARDS */
.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:13px;margin-bottom:24px;
  opacity:0;animation:fadeUp 0.4s ease 0.15s forwards;}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:4px;
  padding:22px 18px;position:relative;overflow:hidden;transition:border-color 0.2s,transform 0.2s;}
.stat:hover{border-color:var(--border2);transform:translateY(-2px);animation:glow-pulse 2s ease-in-out infinite;}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;}
.s-red::before{background:linear-gradient(90deg,var(--red),transparent);}
.s-amber::before{background:linear-gradient(90deg,var(--amber),transparent);}
.s-violet::before{background:linear-gradient(90deg,var(--violet),transparent);}
.s-teal::before{background:linear-gradient(90deg,var(--cyan),transparent);}
.s-orange::before{background:linear-gradient(90deg,var(--orange),transparent);}
.s-green::before{background:linear-gradient(90deg,var(--g),transparent);}
.stat-label{font-size:8px;color:var(--g3);letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;}
.stat-num{font-family:'Orbitron',monospace;font-size:40px;font-weight:900;line-height:1;margin-bottom:4px;}
.s-red .stat-num{color:var(--red);text-shadow:0 0 16px rgba(255,0,64,0.5);}
.s-amber .stat-num{color:var(--amber);text-shadow:0 0 16px rgba(255,170,0,0.5);}
.s-violet .stat-num{color:var(--violet);text-shadow:0 0 16px rgba(168,85,247,0.5);}
.s-teal .stat-num{color:var(--cyan);text-shadow:0 0 16px rgba(0,255,255,0.5);}
.s-orange .stat-num{color:var(--orange);text-shadow:0 0 16px rgba(255,136,0,0.5);}
.s-green .stat-num{color:var(--g);text-shadow:0 0 16px rgba(0,255,65,0.5);}
.stat-sub{font-size:9px;color:var(--muted);}

/* BREAKDOWN */
.breakdown{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:24px;
  opacity:0;animation:fadeUp 0.4s ease 0.25s forwards;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:4px;
  padding:24px 26px;position:relative;overflow:hidden;}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.4;}
.card-title{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--g);
  letter-spacing:2px;margin-bottom:4px;display:flex;align-items:center;gap:10px;}
.card-sub{font-size:9px;color:var(--g3);letter-spacing:2px;margin-bottom:20px;}
.bar-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.bar-label{font-size:9px;color:var(--dim);width:130px;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;letter-spacing:1px;}
.bar-track{flex:1;height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;}
.bar-fill{height:100%;border-radius:2px;animation:bar-grow 1s ease forwards;}
.bar-count{font-size:9px;color:var(--dim);width:24px;text-align:right;flex-shrink:0;}
.bar-pct{font-size:9px;color:var(--g3);width:36px;text-align:right;flex-shrink:0;}

/* LOG TABLE */
.log-section{background:var(--panel);border:1px solid var(--border);border-radius:4px;
  overflow:hidden;opacity:0;animation:fadeUp 0.4s ease 0.35s forwards;position:relative;}
.log-section::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--amber),transparent);opacity:0.5;}
.log-top{display:flex;justify-content:space-between;align-items:center;padding:18px 26px;border-bottom:1px solid var(--border);}
.log-top h3{font-family:'Orbitron',monospace;font-size:12px;font-weight:700;color:var(--amber);
  letter-spacing:3px;text-shadow:0 0 12px rgba(255,170,0,0.4);}
.log-top-right{display:flex;align-items:center;gap:10px;}
.log-count{font-size:9px;color:var(--g3);border:1px solid var(--border);padding:3px 12px;letter-spacing:2px;}
.pdf-btn{font-size:9px;color:var(--amber);text-decoration:none;letter-spacing:1px;
  border:1px solid rgba(255,170,0,0.4);padding:4px 12px;border-radius:2px;transition:all 0.2s;}
.pdf-btn:hover{background:rgba(255,170,0,0.08);box-shadow:0 0 14px rgba(255,170,0,0.3);}

table{width:100%;border-collapse:collapse;}
thead th{padding:10px 18px;text-align:left;font-size:8px;color:var(--g3);letter-spacing:3px;
  text-transform:uppercase;border-bottom:1px solid var(--border);background:var(--bg3);}
tbody tr{border-bottom:1px solid rgba(0,255,65,0.05);transition:background 0.15s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:rgba(0,255,65,0.03);}
td{padding:12px 18px;font-size:11px;color:var(--text);}
.td-mono{font-size:10px;color:var(--dim);}
.td-ip{font-size:10px;color:var(--cyan);font-family:'Share Tech Mono',monospace;}
.td-payload{font-size:9px;color:var(--muted);max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:2px;font-size:8px;letter-spacing:2px;border:1px solid;}
.b-sql{color:var(--red);border-color:rgba(255,0,64,0.3);background:rgba(255,0,64,0.06);}
.b-xss{color:var(--amber);border-color:rgba(255,170,0,0.3);background:rgba(255,170,0,0.06);}
.b-cmd{color:var(--cyan);border-color:rgba(0,255,255,0.3);background:rgba(0,255,255,0.06);}
.b-path{color:var(--orange);border-color:rgba(255,136,0,0.3);background:rgba(255,136,0,0.06);}
.b-unk{color:var(--dim);border-color:var(--border);background:transparent;}
.b-block{color:var(--red);border-color:rgba(255,0,64,0.3);background:rgba(255,0,64,0.06);}

.empty{text-align:center;padding:80px 40px;}
.empty-icon{font-size:48px;opacity:0.15;margin-bottom:16px;}
.empty-t{font-family:'Orbitron',monospace;font-size:14px;color:var(--g3);margin-bottom:8px;letter-spacing:2px;}
.empty-s{font-size:11px;color:var(--muted);}

@media(max-width:900px){.stats{grid-template-columns:repeat(3,1fr);}.breakdown{grid-template-columns:1fr;}main{padding:24px;}}
</style>
""" + MATRIX_JS + """
</head>
<body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>

<nav>
  <div class="nav-left">
    <div class="logo">W-IPS</div>
    <div class="live-badge"><div class="live-dot"></div>REPORT LIVE</div>
  </div>
  <div class="nav-links">
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:8080/login">DEMO</a>
    <a href="http://localhost:5002">DASHBOARD</a>
    <a href="/download/pdf" class="nav-pdf-btn">&#9889; PDF</a>
  </div>
</nav>

<main>
  <div class="page-head">
    <h1>ATTACK <span>REPORT</span></h1>
    <p>REAL-TIME WAF INTRUSION DETECTION &amp; PREVENTION ANALYSIS</p>
    <div class="refresh-row">
      <div class="gen-time">GENERATED: {{ gen_time }}</div>
      <div class="countdown" id="cd">REFRESH IN 10s</div>
    </div>
  </div>

  <div class="stats">
    <div class="stat s-red">
      <div class="stat-label">TOTAL ATTACKS</div>
      <div class="stat-num">{{ total }}</div>
      <div class="stat-sub">all detections</div>
    </div>
    <div class="stat s-amber">
      <div class="stat-label">SQL INJECTION</div>
      <div class="stat-num">{{ type_counts.get('SQL Injection',0) }}</div>
      <div class="stat-sub">db attacks</div>
    </div>
    <div class="stat s-violet">
      <div class="stat-label">XSS</div>
      <div class="stat-num">{{ type_counts.get('XSS',0) }}</div>
      <div class="stat-sub">script injections</div>
    </div>
    <div class="stat s-teal">
      <div class="stat-label">PATH TRAVERSAL</div>
      <div class="stat-num">{{ type_counts.get('Path Traversal',0) }}</div>
      <div class="stat-sub">dir attacks</div>
    </div>
    <div class="stat s-orange">
      <div class="stat-label">CMD INJECTION</div>
      <div class="stat-num">{{ type_counts.get('Command Injection',0) }}</div>
      <div class="stat-sub">shell attacks</div>
    </div>
    <div class="stat s-green">
      <div class="stat-label">IPs BLOCKED</div>
      <div class="stat-num">{{ blocked }}</div>
      <div class="stat-sub">permanent bans</div>
    </div>
  </div>

  <div class="breakdown">
    <div class="card">
      <div class="card-title">&#127919; ATTACK TYPE BREAKDOWN</div>
      <div class="card-sub">DISTRIBUTION BY CATEGORY</div>
      {% for atype, count in type_counts.most_common() %}
      {% set pct = (count / total * 100)|round(1) if total > 0 else 0 %}
      {% if 'SQL' in atype %}{% set clr='#ff0040' %}
      {% elif 'XSS' in atype %}{% set clr='#ffaa00' %}
      {% elif 'Command' in atype %}{% set clr='#00ffff' %}
      {% elif 'Path' in atype %}{% set clr='#ff8800' %}
      {% else %}{% set clr='rgba(0,255,65,0.3)' %}{% endif %}
      <div class="bar-row">
        <div class="bar-label">{{ atype }}</div>
        <div class="bar-track">
          <div class="bar-fill" style="--w:{{ pct }}%;width:{{ pct }}%;background:{{ clr }};"></div>
        </div>
        <div class="bar-count">{{ count }}</div>
        <div class="bar-pct">{{ pct }}%</div>
      </div>
      {% else %}
      <div style="color:var(--muted);font-size:11px;padding:20px 0;">No attack data yet</div>
      {% endfor %}
    </div>

    <div class="card">
      <div class="card-title">&#127760; TOP ATTACKER IPs</div>
      <div class="card-sub">MOST FREQUENT SOURCES</div>
      {% set max_c = ip_counts.most_common(1)[0][1] if ip_counts else 1 %}
      {% for ip, count in ip_counts.most_common(8) %}
      {% set pct = (count / max_c * 100)|round(1) %}
      <div class="bar-row">
        <div class="bar-label">{{ ip }}</div>
        <div class="bar-track">
          <div class="bar-fill" style="--w:{{ pct }}%;width:{{ pct }}%;background:var(--cyan);"></div>
        </div>
        <div class="bar-count">{{ count }}</div>
        <div class="bar-pct">{{ (count/total*100)|round(1) if total > 0 else 0 }}%</div>
      </div>
      {% else %}
      <div style="color:var(--muted);font-size:11px;padding:20px 0;">No IP data yet</div>
      {% endfor %}
    </div>
  </div>

  <div class="log-section">
    <div class="log-top">
      <h3>&#9889; FULL ATTACK LOG</h3>
      <div class="log-top-right">
        <div class="log-count">{{ total }} ENTRIES</div>
        <a href="/download/pdf" class="pdf-btn">&#11015; DOWNLOAD PDF</a>
      </div>
    </div>
    {% if logs %}
    <table>
      <thead>
        <tr><th>#</th><th>TIMESTAMP</th><th>IP ADDRESS</th><th>ATTACK TYPE</th><th>PAYLOAD / URL</th><th>STATUS</th></tr>
      </thead>
      <tbody>
        {% for log in logs|reverse %}
        <tr>
          <td class="td-mono">{{ loop.index }}</td>
          <td class="td-mono">{{ log.time }}</td>
          <td class="td-ip">{{ log.ip }}</td>
          <td>
            {% set t = log.get('attack_type','') or classify_fn(log) %}
            {% if 'SQL' in t %}<span class="badge b-sql">SQL</span>
            {% elif 'XSS' in t %}<span class="badge b-xss">XSS</span>
            {% elif 'Command' in t %}<span class="badge b-cmd">CMD</span>
            {% elif 'Path' in t %}<span class="badge b-path">PATH</span>
            {% else %}<span class="badge b-unk">???</span>{% endif %}
          </td>
          <td class="td-payload" title="{{ log.payload }}">{{ log.payload }}</td>
          <td><span class="badge b-block">BLOCKED</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="empty">
      <div class="empty-icon">&#128737;&#65039;</div>
      <div class="empty-t">NO THREATS LOGGED</div>
      <div class="empty-s">Send test payloads through http://localhost:8080/login</div>
    </div>
    {% endif %}
  </div>
</main>

<script>
var secs = 10;
var cd = document.getElementById('cd');
setInterval(function(){
  secs--;
  if(secs<=0){location.reload();return;}
  cd.textContent = 'REFRESH IN ' + secs + 's';
}, 1000);
</script>
</body>
</html>""")


# ── routes ─────────────────────────────────────────────────────────────────────
@app.route('/')
def report_page():
    logs = load_logs()
    type_counts, ip_counts = get_stats(logs)
    blocked = get_blocked_count()
    gen_time = datetime.now().strftime('%d %b %Y  %H:%M:%S')
    return render_template_string(
        REPORT_HTML,
        logs=logs,
        total=len(logs),
        type_counts=type_counts,
        ip_counts=ip_counts,
        blocked=blocked,
        gen_time=gen_time,
        classify_fn=classify,
    )

@app.route('/download/pdf')
def download_pdf():
    try:
        from fpdf import FPDF # type: ignore
    except ImportError:
        return "fpdf2 not installed. Run: pip install fpdf2", 500

    logs = load_logs()
    type_counts, ip_counts = get_stats(logs)
    total = len(logs)
    blocked = get_blocked_count()
    gen_time = datetime.now().strftime('%d %b %Y  %H:%M:%S')

    class PDF(FPDF):
        def header(self):
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(0, 204, 51)
            self.cell(0, 8, 'WEB APPLICATION FIREWALL - INTRUSION PREVENTION SYSTEM REPORT', align='C')
            self.set_draw_color(0, 204, 51)
            self.line(10, self.get_y() + 8, 200, self.get_y() + 8)
            self.ln(10)
        def footer(self):
            self.set_y(-14)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 116, 139)
            # FIX: replaced em dash (—) with regular hyphen (-) for fpdf2 compatibility
            self.cell(0, 8, f'Page {self.page_no()}  |  Generated: {gen_time}  |  WAF Intrusion Prevention System - SEM 4 Mini Project', align='C')

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Title block
    pdf.set_fill_color(10, 18, 10)
    pdf.rect(10, 14, 190, 30, 'F')
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(0, 255, 65)
    pdf.set_xy(10, 18)
    pdf.cell(190, 10, 'WAF ATTACK REPORT', align='C')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(0, 143, 35)
    pdf.set_xy(10, 31)
    pdf.cell(190, 8, f'Generated: {gen_time}   |   Total Detections: {total}   |   IPs Blocked: {blocked}', align='C')
    pdf.ln(22)

    def section_title(txt):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 204, 51)
        pdf.cell(0, 8, txt, ln=True)
        pdf.set_draw_color(0, 204, 51)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    def key_val(k, v, vcolor=(200, 255, 200)):
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 143, 35)
        pdf.cell(90, 7, k)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*vcolor)
        pdf.cell(0, 7, str(v), ln=True)

    section_title('SUMMARY')
    key_val('Total Attacks Detected',          total,                                    (255, 0,   64))
    key_val('SQL Injection Attempts',          type_counts.get('SQL Injection', 0),      (255, 170, 0))
    key_val('XSS Attacks',                    type_counts.get('XSS', 0),                (168, 85,  247))
    key_val('Command Injection Attempts',      type_counts.get('Command Injection', 0),  (0,  255, 255))
    key_val('Path Traversal Attempts',         type_counts.get('Path Traversal', 0),     (255, 136, 0))
    key_val('Unknown / Uncategorised',         type_counts.get('Unknown', 0),            (100, 116, 139))
    key_val('IPs Permanently Blocked',         blocked,                                  (0,  255, 65))
    pdf.ln(4)

    section_title('ATTACK TYPE BREAKDOWN')
    pdf.set_fill_color(10, 18, 10)
    pdf.set_text_color(0, 143, 35)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(70, 7, 'ATTACK TYPE', fill=True)
    pdf.cell(25, 7, 'COUNT',       fill=True)
    pdf.cell(25, 7, 'PERCENTAGE',  fill=True)
    pdf.cell(0,  7, 'SEVERITY',    fill=True, ln=True)
    color_map = {
        'SQL Injection':    ((255,0,64),   'HIGH'),
        'XSS':              ((255,170,0),  'HIGH'),
        'Command Injection':((0,255,255),  'CRITICAL'),
        'Path Traversal':   ((255,136,0),  'MEDIUM'),
        'Unknown':          ((100,116,139),'LOW'),
    }
    for atype, count in type_counts.most_common():
        pct = f'{round(count/total*100,1)}%' if total > 0 else '0%'
        clr, sev = color_map.get(atype, ((200,255,200), 'LOW'))
        pdf.set_font('Helvetica', '', 9); pdf.set_text_color(200,255,200)
        pdf.cell(70, 6, atype)
        pdf.set_font('Helvetica', 'B', 9); pdf.set_text_color(*clr)
        pdf.cell(25, 6, str(count))
        pdf.cell(25, 6, pct)
        pdf.cell(0,  6, sev, ln=True)
    pdf.ln(4)

    section_title(f'FULL ATTACK LOG  ({total} entries)')
    pdf.set_fill_color(10, 18, 10)
    pdf.set_text_color(0, 143, 35)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(8,  7, '#',            fill=True)
    pdf.cell(44, 7, 'TIMESTAMP',    fill=True)
    pdf.cell(26, 7, 'IP ADDRESS',   fill=True)
    pdf.cell(32, 7, 'ATTACK TYPE',  fill=True)
    pdf.cell(0,  7, 'PAYLOAD / URL',fill=True, ln=True)
    for i, log in enumerate(reversed(logs), 1):
        if pdf.get_y() > 270: pdf.add_page()
        atype = classify(log)
        clr, _ = color_map.get(atype, ((200,255,200), 'LOW'))
        payload = str(log.get('payload',''))[:70]
        pdf.set_font('Helvetica', '', 7); pdf.set_text_color(148,163,184)
        pdf.cell(8,  5.5, str(i))
        pdf.cell(44, 5.5, str(log.get('time',''))[:22])
        pdf.set_text_color(0,204,204)
        pdf.cell(26, 5.5, str(log.get('ip','')))
        pdf.set_text_color(*clr); pdf.set_font('Helvetica','B',7)
        pdf.cell(32, 5.5, atype)
        pdf.set_text_color(100,116,139); pdf.set_font('Helvetica','',7)
        pdf.cell(0,  5.5, payload, ln=True)

    pdf_bytes = bytes(pdf.output())
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'waf_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


if __name__ == '__main__':
    print()
    print('  +======================================+')
    print('  |  WAF Report Server  --  Port 5003   |')
    print('  +======================================+')
    print()
    app.run(port=5003, debug=False)
