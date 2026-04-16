"""
report.py - WAF Attack Report + PDF Export (Port 5003)
Routes:
  /              -> live report page
  /download/pdf  -> clean PDF download
"""
from flask import Flask, render_template_string, send_file, redirect
import json, os, io
from datetime import datetime
from collections import Counter

app = Flask(__name__)
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
LOG_FILE   = os.path.join(BASE_DIR, 'attacks.log')
BLOCK_FILE = os.path.join(BASE_DIR, 'blocked_ips.json')

def load_logs():
    logs = []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                l = line.strip()
                if l:
                    try: logs.append(json.loads(l))
                    except: pass
    except: pass
    return logs

def classify(log):
    t = log.get('attack_type', '')
    if t: return t
    p = log.get('payload', '').lower()
    if any(x in p for x in [' or ', 'union select', 'drop table', 'sleep(', '--']): return 'SQL Injection'
    if any(x in p for x in ['<script', 'javascript:', 'onerror=', 'alert(']): return 'XSS'
    if any(x in p for x in ['; ls', '| whoami', '&&']): return 'Command Injection'
    if any(x in p for x in ['../', 'etc/passwd']): return 'Path Traversal'
    return 'Unknown'

def get_blocked():
    try:
        with open(BLOCK_FILE) as f:
            return len(json.load(f).get('blocked_ips', []))
    except: return 0

# Redirect / to backend report route
@app.route('/')
def report_redirect():
    logs = load_logs()
    type_counts = Counter(classify(l) for l in logs)
    ip_counts   = Counter(l.get('ip','?') for l in logs)
    blocked     = get_blocked()
    total       = len(logs)
    gen_time    = datetime.now().strftime('%d %b %Y  %H:%M:%S')
    return render_template_string(REPORT_HTML,
        logs=logs, total=total, type_counts=type_counts,
        ip_counts=ip_counts, blocked=blocked, gen_time=gen_time,
        classify_fn=classify)

MATRIX_JS = r"""
<script>
window.addEventListener('DOMContentLoaded', function() {
  var cv=document.getElementById('matrix'),ctx=cv.getContext('2d');
  var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(){}[]';
  var W,H,cols,drops;
  function init(){W=cv.width=innerWidth;H=cv.height=innerHeight;cols=Math.floor(W/16);drops=[];for(var i=0;i<cols;i++)drops[i]=Math.random()*-50;}
  init();window.addEventListener('resize',init);
  setInterval(function(){
    ctx.fillStyle='rgba(5,10,5,0.05)';ctx.fillRect(0,0,W,H);
    for(var i=0;i<drops.length;i++){var ch=chars[Math.floor(Math.random()*chars.length)],x=i*16,y=drops[i]*16;
      ctx.fillStyle='#ccffcc';ctx.font='bold 13px monospace';ctx.fillText(ch,x,y);
      ctx.fillStyle='#00ff41';ctx.font='12px monospace';
      if(Math.random()>0.5&&y>16)ctx.fillText(chars[Math.floor(Math.random()*chars.length)],x,y-16);
      if(y>H&&Math.random()>0.975)drops[i]=0;drops[i]++;}
  },45);
});
</script>
"""

REPORT_HTML = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Attack Report</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#050a05;--bg2:#070d07;--bg3:#0a120a;--panel:#0c160c;
  --border:rgba(0,255,65,0.15);--border2:rgba(0,255,65,0.35);
  --g:#00ff41;--g2:#00cc33;--g3:#008f23;--dim:rgba(0,255,65,0.45);
  --red:#ff0040;--amber:#ffaa00;--cyan:#00ffff;--violet:#a855f7;--orange:#ff8800;--text:#c8ffc8;}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Share Tech Mono',monospace;background:var(--bg);color:var(--g);min-height:100vh;overflow-x:hidden;}
#matrix{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.1;}
body::after{content:'';position:fixed;inset:0;z-index:999;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.07) 2px,rgba(0,0,0,0.07) 4px);}
body::before{content:'';position:fixed;inset:0;z-index:998;pointer-events:none;background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.55) 100%);}
@keyframes glitch{0%,100%{text-shadow:none;transform:none;}20%{text-shadow:-2px 0 #ff0040,2px 0 #00ffff;transform:translate(-1px,0);}40%{text-shadow:2px 0 #ff0040,-2px 0 #00ffff;transform:translate(1px,0);}60%{text-shadow:none;transform:none;}80%{text-shadow:-1px 0 #00ffff;transform:translate(1px,0);}}
@keyframes flicker{0%,100%{opacity:1}42%{opacity:0.6}76%{opacity:0.7}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
@keyframes scanH{0%{top:-4px}100%{top:100%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes bar-grow{from{width:0}to{width:var(--w)}}
.scan-line{position:fixed;left:0;right:0;height:2px;z-index:997;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(0,255,65,0.35),transparent);animation:scanH 8s linear infinite;}
nav{position:sticky;top:0;z-index:200;display:flex;justify-content:space-between;align-items:center;padding:12px 40px;background:rgba(5,10,5,0.93);backdrop-filter:blur(14px);border-bottom:1px solid var(--border);animation:flicker 10s infinite;}
.logo{font-family:'Orbitron',monospace;font-size:13px;font-weight:900;color:var(--g);letter-spacing:4px;text-shadow:0 0 20px var(--g);animation:glitch 7s infinite;text-decoration:none;}
.nav-links{display:flex;gap:6px;align-items:center;}
.nav-link{font-size:9px;color:var(--dim);text-decoration:none;letter-spacing:1.5px;padding:5px 10px;border:1px solid transparent;border-radius:2px;transition:all 0.2s;}
.nav-link:hover{color:var(--g);border-color:var(--border);}
.nav-pdf{color:var(--amber);border-color:rgba(255,170,0,0.3) !important;}
.nav-pdf:hover{color:var(--amber) !important;background:rgba(255,170,0,0.06) !important;}
main{position:relative;z-index:1;max-width:1300px;margin:0 auto;padding:40px 44px 60px;}
.page-head{margin-bottom:30px;opacity:0;animation:fadeUp 0.5s ease 0.1s forwards;}
.page-head h1{font-family:'Orbitron',monospace;font-size:26px;font-weight:900;letter-spacing:2px;text-shadow:0 0 20px rgba(0,255,65,0.4);margin-bottom:4px;}
.page-head h1 span{color:var(--amber);text-shadow:0 0 18px rgba(255,170,0,0.5);}
.page-head p{font-size:10px;color:var(--dim);letter-spacing:1px;}
.refresh-row{display:flex;align-items:center;gap:12px;margin-top:6px;}
.gen-t{font-size:9px;color:var(--g3);letter-spacing:1px;}
.cd{font-size:9px;color:var(--amber);border:1px solid rgba(255,170,0,0.3);padding:2px 10px;letter-spacing:1px;}
.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:18px;opacity:0;animation:fadeUp 0.4s ease 0.15s forwards;}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:18px 14px;text-align:center;position:relative;overflow:hidden;transition:all 0.2s;}
.stat:hover{border-color:var(--border2);transform:translateY(-2px);}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;}
.s-r::before{background:linear-gradient(90deg,var(--red),transparent);}
.s-a::before{background:linear-gradient(90deg,var(--amber),transparent);}
.s-v::before{background:linear-gradient(90deg,var(--violet),transparent);}
.s-c::before{background:linear-gradient(90deg,var(--cyan),transparent);}
.s-o::before{background:linear-gradient(90deg,var(--orange),transparent);}
.s-g::before{background:linear-gradient(90deg,var(--g),transparent);}
.stat-n{font-family:'Orbitron',monospace;font-size:36px;font-weight:900;line-height:1;margin-bottom:5px;}
.s-r .stat-n{color:var(--red);}
.s-a .stat-n{color:var(--amber);}
.s-v .stat-n{color:var(--violet);}
.s-c .stat-n{color:var(--cyan);}
.s-o .stat-n{color:var(--orange);}
.s-g .stat-n{color:var(--g);}
.stat-l{font-size:7px;color:var(--g3);letter-spacing:2px;text-transform:uppercase;}
.breakdown{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px;opacity:0;animation:fadeUp 0.4s ease 0.25s forwards;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:22px 24px;position:relative;overflow:hidden;}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.4;}
.card-title{font-family:'Orbitron',monospace;font-size:10px;font-weight:700;color:var(--g);letter-spacing:2px;margin-bottom:3px;}
.card-sub{font-size:8px;color:var(--g3);letter-spacing:1px;margin-bottom:18px;}
.bar-row{display:flex;align-items:center;gap:8px;margin-bottom:9px;}
.bar-label{font-size:9px;color:var(--dim);width:120px;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.bar-track{flex:1;height:4px;background:var(--bg3);border-radius:2px;overflow:hidden;}
.bar-fill{height:100%;border-radius:2px;animation:bar-grow 0.8s ease forwards;}
.bar-n{font-size:9px;color:var(--dim);width:22px;text-align:right;flex-shrink:0;}
.bar-p{font-size:9px;color:var(--g3);width:34px;text-align:right;flex-shrink:0;}
.log-section{background:var(--panel);border:1px solid var(--border);border-radius:4px;overflow:hidden;opacity:0;animation:fadeUp 0.4s ease 0.35s forwards;position:relative;}
.log-section::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--amber),transparent);opacity:0.5;}
.log-top{display:flex;justify-content:space-between;align-items:center;padding:16px 22px;border-bottom:1px solid var(--border);}
.log-top h3{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--amber);letter-spacing:3px;text-shadow:0 0 10px rgba(255,170,0,0.4);}
.log-right{display:flex;align-items:center;gap:8px;}
.pill{font-size:8px;color:var(--g3);border:1px solid var(--border);padding:2px 10px;letter-spacing:1px;}
.pdf-link{font-size:8px;color:var(--amber);text-decoration:none;border:1px solid rgba(255,170,0,0.4);padding:4px 12px;border-radius:2px;transition:all 0.2s;}
.pdf-link:hover{background:rgba(255,170,0,0.08);}
table{width:100%;border-collapse:collapse;}
thead th{padding:9px 14px;text-align:left;font-size:7px;color:var(--g3);letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid var(--border);background:var(--bg3);}
tbody tr{border-bottom:1px solid rgba(0,255,65,0.05);transition:background 0.15s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:rgba(0,255,65,0.03);}
td{padding:10px 14px;font-size:10px;color:var(--text);}
.td-m{font-size:9px;color:var(--dim);}
.td-ip{font-size:10px;color:var(--cyan);}
.td-p{font-size:8px;color:var(--muted,rgba(0,255,65,0.3));max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.badge{display:inline-flex;align-items:center;padding:2px 7px;border-radius:2px;font-size:7px;letter-spacing:1px;border:1px solid;}
.b-sql{color:var(--red);border-color:rgba(255,0,64,0.3);background:rgba(255,0,64,0.06);}
.b-xss{color:var(--amber);border-color:rgba(255,170,0,0.3);background:rgba(255,170,0,0.06);}
.b-cmd{color:var(--cyan);border-color:rgba(0,255,255,0.3);background:rgba(0,255,255,0.06);}
.b-path{color:var(--orange);border-color:rgba(255,136,0,0.3);background:rgba(255,136,0,0.06);}
.b-block{color:var(--red);border-color:rgba(255,0,64,0.3);background:rgba(255,0,64,0.06);}
.b-unk{color:var(--dim);border-color:var(--border);}
.sev-b{display:inline-block;padding:2px 6px;border-radius:2px;font-size:7px;letter-spacing:1px;border:1px solid;}
.sev-CRITICAL{color:var(--red);border-color:rgba(255,0,64,0.4);background:rgba(255,0,64,0.07);}
.sev-HIGH{color:var(--amber);border-color:rgba(255,170,0,0.4);background:rgba(255,170,0,0.07);}
.sev-MEDIUM{color:var(--cyan);border-color:rgba(0,255,255,0.3);background:rgba(0,255,255,0.05);}
.sev-LOW{color:var(--g);border-color:rgba(0,255,65,0.3);background:rgba(0,255,65,0.05);}
.empty{text-align:center;padding:60px;color:var(--dim);font-size:11px;}
@media(max-width:900px){.stats{grid-template-columns:repeat(3,1fr);}.breakdown{grid-template-columns:1fr;}main{padding:24px;}}
</style>""" + MATRIX_JS + """
</head><body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<nav>
  <a href="http://localhost:5001" class="logo">W-IPS</a>
  <div class="nav-links">
    <a href="http://localhost:5001" class="nav-link">HOME</a>
    <a href="http://localhost:5001/dashboard" class="nav-link">DASHBOARD</a>
    <a href="http://localhost:5001/simulate" class="nav-link">SIMULATOR</a>
    <a href="/download/pdf" class="nav-link nav-pdf">&#11015; PDF</a>
  </div>
</nav>
<main>
  <div class="page-head">
    <h1>ATTACK <span>REPORT</span></h1>
    <p>REAL-TIME WAF INTRUSION DETECTION ANALYSIS</p>
    <div class="refresh-row">
      <div class="gen-t">GENERATED: {{ gen_time }}</div>
      <div class="cd" id="cd">REFRESH IN 10s</div>
    </div>
  </div>

  <div class="stats">
    <div class="stat s-r"><div class="stat-n">{{ total }}</div><div class="stat-l">Total</div></div>
    <div class="stat s-a"><div class="stat-n">{{ type_counts.get('SQL Injection',0) }}</div><div class="stat-l">SQL</div></div>
    <div class="stat s-v"><div class="stat-n">{{ type_counts.get('XSS',0) }}</div><div class="stat-l">XSS</div></div>
    <div class="stat s-c"><div class="stat-n">{{ type_counts.get('Path Traversal',0) }}</div><div class="stat-l">Path</div></div>
    <div class="stat s-o"><div class="stat-n">{{ type_counts.get('Command Injection',0) }}</div><div class="stat-l">CMD</div></div>
    <div class="stat s-g"><div class="stat-n">{{ blocked }}</div><div class="stat-l">Blocked IPs</div></div>
  </div>

  <div class="breakdown">
    <div class="card">
      <div class="card-title">ATTACK TYPE BREAKDOWN</div>
      <div class="card-sub">DISTRIBUTION BY CATEGORY</div>
      {% for atype, count in type_counts.most_common() %}
      {% set pct = (count/total*100)|round(1) if total>0 else 0 %}
      {% if 'SQL' in atype %}{% set clr='#ff0040' %}
      {% elif 'XSS' in atype %}{% set clr='#ffaa00' %}
      {% elif 'Command' in atype %}{% set clr='#00ffff' %}
      {% elif 'Path' in atype %}{% set clr='#ff8800' %}
      {% elif 'Honeypot' in atype %}{% set clr='#ffaa00' %}
      {% else %}{% set clr='rgba(0,255,65,0.3)' %}{% endif %}
      <div class="bar-row">
        <div class="bar-label">{{ atype }}</div>
        <div class="bar-track"><div class="bar-fill" style="--w:{{ pct }}%;width:{{ pct }}%;background:{{ clr }};"></div></div>
        <div class="bar-n">{{ count }}</div>
        <div class="bar-p">{{ pct }}%</div>
      </div>
      {% else %}<div style="color:var(--dim);font-size:10px;padding:10px 0;">No attack data yet</div>{% endfor %}
    </div>
    <div class="card">
      <div class="card-title">TOP ATTACKER IPs</div>
      <div class="card-sub">MOST FREQUENT SOURCES</div>
      {% set max_c = ip_counts.most_common(1)[0][1] if ip_counts else 1 %}
      {% for ip, count in ip_counts.most_common(8) %}
      {% set pct = (count/max_c*100)|round(1) %}
      <div class="bar-row">
        <div class="bar-label">{{ ip }}</div>
        <div class="bar-track"><div class="bar-fill" style="--w:{{ pct }}%;width:{{ pct }}%;background:var(--cyan);"></div></div>
        <div class="bar-n">{{ count }}</div>
        <div class="bar-p">{{ (count/total*100)|round(1) if total>0 else 0 }}%</div>
      </div>
      {% else %}<div style="color:var(--dim);font-size:10px;padding:10px 0;">No IP data yet</div>{% endfor %}
    </div>
  </div>

  <div class="log-section">
    <div class="log-top">
      <h3>FULL ATTACK LOG</h3>
      <div class="log-right">
        <div class="pill">{{ total }} ENTRIES</div>
        <a href="/download/pdf" class="pdf-link">&#11015; DOWNLOAD PDF</a>
      </div>
    </div>
    {% if logs %}
    <table>
      <thead><tr><th>#</th><th>TIMESTAMP</th><th>IP ADDRESS</th><th>COUNTRY</th><th>TYPE</th><th>SEVERITY</th><th>PAYLOAD</th><th>STATUS</th></tr></thead>
      <tbody>
        {% for log in logs|reverse %}
        <tr>
          <td class="td-m">{{ loop.index }}</td>
          <td class="td-m">{{ log.time }}</td>
          <td class="td-ip">{{ log.ip }}</td>
          <td class="td-m">{{ log.get('country','?') }}</td>
          <td>{% set t=log.get('attack_type','') or classify_fn(log) %}
            {% if 'SQL' in t %}<span class="badge b-sql">SQL</span>
            {% elif 'XSS' in t %}<span class="badge b-xss">XSS</span>
            {% elif 'Command' in t %}<span class="badge b-cmd">CMD</span>
            {% elif 'Path' in t %}<span class="badge b-path">PATH</span>
            {% else %}<span class="badge b-unk">???</span>{% endif %}
          </td>
          <td><span class="sev-b sev-{{ log.get('severity','LOW') }}">{{ log.get('severity','LOW') }}</span></td>
          <td class="td-p" title="{{ log.payload }}">{{ log.payload }}</td>
          <td><span class="badge b-block">BLOCKED</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}<div class="empty">No attacks logged yet — send payloads from /login</div>{% endif %}
  </div>
</main>
<script>
var s=10,cd=document.getElementById('cd');
setInterval(function(){s--;if(s<=0){location.reload();return;}cd.textContent='REFRESH IN '+s+'s';},1000);
</script>
</body></html>"""


@app.route('/download/pdf')
def download_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        return "fpdf2 not installed. Run: pip install fpdf2", 500

    logs       = load_logs()
    total      = len(logs)
    blocked    = get_blocked()
    gen_time   = datetime.now().strftime('%d %b %Y  %H:%M:%S')
    type_counts= Counter(classify(l) for l in logs)
    ip_counts  = Counter(l.get('ip','?') for l in logs)

    color_map = {
        'SQL Injection':    ((220, 50,  50),  'CRITICAL'),
        'XSS':              ((220,150,  30),  'HIGH'),
        'Command Injection':((30, 180, 180),  'CRITICAL'),
        'Path Traversal':   ((220,120,  30),  'HIGH'),
        'Honeypot':         ((200,150,  30),  'CRITICAL'),
        'Brute Force':      ((150, 80, 200),  'HIGH'),
        'Unknown':          ((120,130,140),   'LOW'),
    }

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(15, 15, 15)

    # ── PAGE 1: Cover ─────────────────────────────────────────────────────────
    pdf.add_page()

    # Header bar
    pdf.set_fill_color(10, 25, 10)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(0, 220, 60)
    pdf.set_xy(0, 10)
    pdf.cell(210, 10, 'WEB APPLICATION IPS', align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(0, 150, 40)
    pdf.set_xy(0, 22)
    pdf.cell(210, 10, 'Intrusion Prevention System - Attack Report', align='C')
    pdf.ln(30)

    # Meta info box
    pdf.set_fill_color(15, 30, 15)
    pdf.rect(15, 45, 180, 36, 'F')
    pdf.set_draw_color(0, 180, 50)
    pdf.rect(15, 45, 180, 36)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(0, 180, 50)
    pdf.set_xy(20, 49)
    pdf.cell(80, 6, 'Generated:')
    pdf.set_text_color(200, 255, 200)
    pdf.cell(0, 6, gen_time, ln=True)
    pdf.set_xy(20, 57)
    pdf.set_text_color(0, 180, 50)
    pdf.cell(80, 6, 'Total Attacks Detected:')
    pdf.set_text_color(220, 50, 50)
    pdf.cell(0, 6, str(total), ln=True)
    pdf.set_xy(20, 65)
    pdf.set_text_color(0, 180, 50)
    pdf.cell(80, 6, 'IPs Permanently Blocked:')
    pdf.set_text_color(0, 220, 60)
    pdf.cell(0, 6, str(blocked), ln=True)
    pdf.ln(20)

    # Summary stats grid
    def section_hdr(txt):
        pdf.set_fill_color(10, 25, 10)
        pdf.rect(15, pdf.get_y(), 180, 8, 'F')
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 220, 60)
        pdf.cell(180, 8, '  ' + txt, ln=True)
        pdf.set_draw_color(0, 180, 50)
        pdf.set_line_width(0.3)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

    section_hdr('SUMMARY')
    rows = [
        ('Total Attacks Detected', str(total), (220, 50, 50)),
        ('SQL Injection Attempts', str(type_counts.get('SQL Injection',0)), (220,150,30)),
        ('XSS Attacks', str(type_counts.get('XSS',0)), (150, 80,200)),
        ('Command Injection', str(type_counts.get('Command Injection',0)), (30,180,180)),
        ('Path Traversal', str(type_counts.get('Path Traversal',0)), (220,120,30)),
        ('Honeypot Triggers', str(type_counts.get('Honeypot',0)), (220,150,30)),
        ('Brute Force Attempts', str(type_counts.get('Brute Force',0)), (150, 80,200)),
        ('Unknown/Other', str(type_counts.get('Unknown',0)), (120,130,140)),
        ('IPs Permanently Blocked', str(blocked), (0,200,60)),
    ]
    for label, val, clr in rows:
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(140, 180, 140)
        pdf.set_x(15)
        pdf.cell(120, 6, label)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*clr)
        pdf.cell(0, 6, val, ln=True)
    pdf.ln(6)

    # ── PAGE 2: Attack Breakdown + Top IPs ───────────────────────────────────
    section_hdr('ATTACK TYPE BREAKDOWN')
    # Table header
    pdf.set_fill_color(10, 30, 10)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(0, 180, 50)
    pdf.set_x(15)
    pdf.cell(70, 7, 'ATTACK TYPE', fill=True)
    pdf.cell(25, 7, 'COUNT',       fill=True)
    pdf.cell(30, 7, 'PERCENTAGE',  fill=True)
    pdf.cell(0,  7, 'SEVERITY',    fill=True, ln=True)

    for atype, count in type_counts.most_common():
        if pdf.get_y() > 260: pdf.add_page()
        pct = f'{round(count/total*100,1)}%' if total > 0 else '0%'
        clr, sev = color_map.get(atype, ((120,130,140), 'LOW'))
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(180, 220, 180)
        pdf.set_x(15)
        pdf.cell(70, 6, atype)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(*clr)
        pdf.cell(25, 6, str(count))
        pdf.cell(30, 6, pct)
        pdf.cell(0,  6, sev, ln=True)
    pdf.ln(6)

    section_hdr('TOP ATTACKER IPs')
    pdf.set_fill_color(10, 30, 10)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(0, 180, 50)
    pdf.set_x(15)
    pdf.cell(60, 7, 'IP ADDRESS',  fill=True)
    pdf.cell(30, 7, 'ATTACKS',     fill=True)
    pdf.cell(30, 7, 'PERCENTAGE',  fill=True)
    pdf.cell(0,  7, 'COUNTRY',     fill=True, ln=True)

    # Build IP to country mapping
    ip_country = {}
    for l in logs:
        ip = l.get('ip','?')
        if ip not in ip_country:
            ip_country[ip] = l.get('country','Unknown')

    for ip, count in ip_counts.most_common(10):
        if pdf.get_y() > 260: pdf.add_page()
        pct = f'{round(count/total*100,1)}%' if total > 0 else '0%'
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(30, 180, 180)
        pdf.set_x(15)
        pdf.cell(60, 6, ip)
        pdf.set_text_color(220, 50, 50)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(30, 6, str(count))
        pdf.set_text_color(180, 220, 180)
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(30, 6, pct)
        pdf.cell(0,  6, ip_country.get(ip,'Unknown'), ln=True)
    pdf.ln(6)

    # ── PAGE 3+: Full Attack Log ──────────────────────────────────────────────
    if logs:
        pdf.add_page()
        section_hdr(f'FULL ATTACK LOG  ({total} entries)')

        # Column widths that fit in 180mm usable width
        # #(8) | Time(38) | IP(28) | Country(24) | Type(28) | Sev(20) | Payload(34)
        col_w = [8, 38, 28, 24, 28, 20, 34]

        pdf.set_fill_color(10, 30, 10)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_text_color(0, 180, 50)
        pdf.set_x(15)
        for txt, w in zip(['#','TIMESTAMP','IP ADDRESS','COUNTRY','TYPE','SEVERITY','PAYLOAD'], col_w):
            pdf.cell(w, 6, txt, fill=True)
        pdf.ln()

        for idx, log in enumerate(reversed(logs), 1):
            if pdf.get_y() > 268:
                pdf.add_page()
                # Repeat header
                pdf.set_fill_color(10, 30, 10)
                pdf.set_font('Helvetica', 'B', 7)
                pdf.set_text_color(0, 180, 50)
                pdf.set_x(15)
                for txt, w in zip(['#','TIMESTAMP','IP ADDRESS','COUNTRY','TYPE','SEVERITY','PAYLOAD'], col_w):
                    pdf.cell(w, 6, txt, fill=True)
                pdf.ln()

            atype = classify(log)
            clr, sev = color_map.get(atype, ((120,130,140),'LOW'))

            # Truncate fields to fit columns
            timestamp = str(log.get('time',''))[:20]
            ip        = str(log.get('ip',''))[:15]
            country   = str(log.get('country','?'))[:12]
            atype_s   = atype[:14]
            severity  = str(log.get('severity','LOW'))[:8]
            payload   = str(log.get('payload',''))[:22]

            pdf.set_font('Helvetica', '', 7)
            pdf.set_x(15)

            pdf.set_text_color(120,130,140)
            pdf.cell(col_w[0], 5, str(idx))

            pdf.set_text_color(120,140,120)
            pdf.cell(col_w[1], 5, timestamp)

            pdf.set_text_color(30,180,180)
            pdf.cell(col_w[2], 5, ip)

            pdf.set_text_color(120,140,120)
            pdf.cell(col_w[3], 5, country)

            pdf.set_text_color(*clr)
            pdf.set_font('Helvetica','B',7)
            pdf.cell(col_w[4], 5, atype_s)

            pdf.set_font('Helvetica','',7)
            sev_colors = {'CRITICAL':(220,50,50),'HIGH':(220,150,30),'MEDIUM':(30,180,180),'LOW':(0,180,50)}
            pdf.set_text_color(*sev_colors.get(severity,(120,130,140)))
            pdf.cell(col_w[5], 5, severity)

            pdf.set_text_color(100,130,100)
            pdf.cell(col_w[6], 5, payload, ln=True)

    # Footer on all pages
    pdf.alias_nb_pages()

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
    print('  |  http://localhost:5003               |')
    print('  +======================================+')
    print()
    app.run(port=5003, debug=False)