from flask import Flask, render_template_string
import json, os

app = Flask(__name__)

DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Attack Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
<style>
:root{--bg:#050a05;--bg2:#070d07;--bg3:#0a120a;--panel:#0c160c;
  --border:rgba(0,255,65,0.15);--border2:rgba(0,255,65,0.35);
  --g:#00ff41;--g2:#00cc33;--g3:#008f23;--dim:rgba(0,255,65,0.45);--muted:rgba(0,255,65,0.3);
  --red:#ff0040;--amber:#ffaa00;--cyan:#00ffff;--violet:#a855f7;--orange:#ff8800;--text:#c8ffc8;}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Share Tech Mono',monospace;background:var(--bg);color:var(--g);min-height:100vh;overflow-x:hidden;}
#matrix{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.1;}
body::after{content:'';position:fixed;inset:0;z-index:999;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.07) 2px,rgba(0,0,0,0.07) 4px);}
body::before{content:'';position:fixed;inset:0;z-index:998;pointer-events:none;background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.55) 100%);}
@keyframes glitch{0%,100%{text-shadow:none;transform:none;}20%{text-shadow:-2px 0 #ff0040,2px 0 #00ffff;transform:translate(-1px,0);}40%{text-shadow:2px 0 #ff0040,-2px 0 #00ffff;transform:translate(1px,0);}60%{text-shadow:none;transform:none;}80%{text-shadow:-1px 0 #00ffff;transform:translate(1px,0);}}
@keyframes flicker{0%,100%{opacity:1}41%{opacity:1}42%{opacity:0.6}43%{opacity:1}75%{opacity:1}76%{opacity:0.7}77%{opacity:1}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
@keyframes scanH{0%{top:-4px}100%{top:100%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow-pulse{0%,100%{box-shadow:0 0 8px rgba(0,255,65,0.25),inset 0 0 6px rgba(0,255,65,0.04)}50%{box-shadow:0 0 18px rgba(0,255,65,0.5),inset 0 0 12px rgba(0,255,65,0.08)}}
.scan-line{position:fixed;left:0;right:0;height:2px;z-index:997;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(0,255,65,0.35),transparent);animation:scanH 8s linear infinite;}

nav{position:sticky;top:0;z-index:200;display:flex;justify-content:space-between;align-items:center;padding:14px 48px;background:rgba(5,10,5,0.93);backdrop-filter:blur(14px);border-bottom:1px solid var(--border);animation:flicker 10s infinite;}
.logo{font-family:'Orbitron',monospace;font-size:14px;font-weight:900;color:var(--g);letter-spacing:4px;text-shadow:0 0 20px var(--g),0 0 40px rgba(0,255,65,0.3);animation:glitch 7s infinite;}
.nav-left{display:flex;align-items:center;gap:20px;}
.live-badge{display:flex;align-items:center;gap:7px;font-size:9px;color:var(--dim);border:1px solid var(--border);padding:4px 12px;border-radius:2px;letter-spacing:2px;}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--g);box-shadow:0 0 8px var(--g);animation:blink 1s ease-in-out infinite;}
.nav-links{display:flex;gap:24px;align-items:center;}
.nav-links a{font-size:10px;color:var(--dim);text-decoration:none;letter-spacing:2px;transition:color 0.2s,text-shadow 0.2s;}
.nav-links a:hover{color:var(--g);text-shadow:0 0 8px var(--g);}
.refresh-btn{font-size:9px;color:var(--g3);border:1px solid var(--border);padding:4px 12px;cursor:pointer;background:transparent;font-family:'Share Tech Mono',monospace;letter-spacing:1px;transition:all 0.2s;}
.refresh-btn:hover{border-color:var(--border2);color:var(--g);}

main{position:relative;z-index:1;max-width:1400px;margin:0 auto;padding:44px 48px;}

.page-head{margin-bottom:36px;opacity:0;animation:fadeUp 0.5s ease 0.1s forwards;}
.page-head h1{font-family:'Orbitron',monospace;font-size:30px;font-weight:900;letter-spacing:2px;text-shadow:0 0 24px rgba(0,255,65,0.4);margin-bottom:6px;}
.page-head p{font-size:11px;color:var(--dim);letter-spacing:1px;}
.time-info{font-size:10px;color:var(--g3);margin-top:6px;letter-spacing:2px;}

/* STAT CARDS */
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:13px;margin-bottom:24px;opacity:0;animation:fadeUp 0.4s ease 0.15s forwards;}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:22px 18px;position:relative;overflow:hidden;transition:border-color 0.2s,transform 0.2s;}
.stat:hover{border-color:var(--border2);transform:translateY(-2px);animation:glow-pulse 2s ease-in-out infinite;}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;}
.stat-r::before{background:linear-gradient(90deg,var(--red),transparent);}
.stat-a::before{background:linear-gradient(90deg,var(--amber),transparent);}
.stat-c::before{background:linear-gradient(90deg,var(--cyan),transparent);}
.stat-g::before{background:linear-gradient(90deg,var(--g),transparent);}
.stat-v::before{background:linear-gradient(90deg,var(--violet),transparent);}
.stat-label{font-size:8px;color:var(--g3);letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;}
.stat-num{font-family:'Orbitron',monospace;font-size:44px;font-weight:900;line-height:1;margin-bottom:4px;}
.stat-r .stat-num{color:var(--red);text-shadow:0 0 16px rgba(255,0,64,0.5);}
.stat-a .stat-num{color:var(--amber);text-shadow:0 0 16px rgba(255,170,0,0.5);}
.stat-c .stat-num{color:var(--cyan);text-shadow:0 0 16px rgba(0,255,255,0.5);}
.stat-g .stat-num{color:var(--g);text-shadow:0 0 16px rgba(0,255,65,0.5);}
.stat-v .stat-num{color:var(--violet);text-shadow:0 0 16px rgba(168,85,247,0.5);}
.stat-sub{font-size:9px;color:var(--muted);}

/* SEVERITY BAR */
.sev-row{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-bottom:24px;opacity:0;animation:fadeUp 0.4s ease 0.2s forwards;}
.sev-card{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:16px 20px;display:flex;align-items:center;gap:14px;}
.sev-icon{font-size:20px;}
.sev-info{flex:1;}
.sev-label{font-size:8px;color:var(--g3);letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;}
.sev-count{font-family:'Orbitron',monospace;font-size:24px;font-weight:900;}
.sev-critical .sev-count{color:var(--red);text-shadow:0 0 10px rgba(255,0,64,0.5);}
.sev-high .sev-count{color:var(--amber);text-shadow:0 0 10px rgba(255,170,0,0.5);}
.sev-medium .sev-count{color:var(--cyan);text-shadow:0 0 10px rgba(0,255,255,0.5);}
.sev-low .sev-count{color:var(--g);text-shadow:0 0 10px rgba(0,255,65,0.5);}

/* CHARTS */
.charts{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:24px;opacity:0;animation:fadeUp 0.4s ease 0.3s forwards;}
.chart-card{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:28px;position:relative;overflow:hidden;}
.chart-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.4;}
.chart-card h3{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--g);letter-spacing:3px;margin-bottom:4px;}
.chart-card p{font-size:9px;color:var(--g3);letter-spacing:1px;margin-bottom:24px;}
.chart-wrap{position:relative;height:200px;}

/* GEO TABLE */
.geo-section{background:var(--panel);border:1px solid var(--border);border-radius:4px;overflow:hidden;margin-bottom:24px;opacity:0;animation:fadeUp 0.4s ease 0.35s forwards;position:relative;}
.geo-section::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:0.5;}
.section-head{display:flex;justify-content:space-between;align-items:center;padding:18px 26px;border-bottom:1px solid var(--border);}
.section-head h3{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--cyan);letter-spacing:3px;text-shadow:0 0 12px rgba(0,255,255,0.4);}
.geo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1px;background:var(--border);}
.geo-item{background:var(--panel);padding:14px 18px;display:flex;align-items:center;gap:12px;transition:background 0.15s;}
.geo-item:hover{background:var(--bg3);}
.geo-flag{font-size:20px;}
.geo-info{flex:1;}
.geo-country{font-size:11px;color:var(--text);margin-bottom:2px;}
.geo-count{font-family:'Orbitron',monospace;font-size:10px;color:var(--cyan);}

/* HONEYPOT SECTION */
.honeypot-section{background:var(--panel);border:1px solid rgba(255,170,0,0.25);border-radius:4px;overflow:hidden;margin-bottom:24px;opacity:0;animation:fadeUp 0.4s ease 0.4s forwards;position:relative;}
.honeypot-section::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--amber),transparent);opacity:0.6;}
.hp-head h3{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--amber);letter-spacing:3px;text-shadow:0 0 12px rgba(255,170,0,0.4);}

/* LOG TABLE */
.log-section{background:var(--panel);border:1px solid var(--border);border-radius:4px;overflow:hidden;opacity:0;animation:fadeUp 0.4s ease 0.5s forwards;position:relative;}
.log-section::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--amber),transparent);opacity:0.4;}
.log-top{display:flex;justify-content:space-between;align-items:center;padding:18px 26px;border-bottom:1px solid var(--border);}
.log-top h3{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--amber);letter-spacing:3px;text-shadow:0 0 12px rgba(255,170,0,0.4);}
.log-count{font-size:9px;color:var(--g3);border:1px solid var(--border);padding:3px 12px;letter-spacing:2px;}

table{width:100%;border-collapse:collapse;}
thead th{padding:10px 16px;text-align:left;font-size:8px;color:var(--g3);letter-spacing:3px;text-transform:uppercase;border-bottom:1px solid var(--border);background:var(--bg3);}
tbody tr{border-bottom:1px solid rgba(0,255,65,0.05);transition:background 0.15s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:rgba(0,255,65,0.03);}
td{padding:11px 16px;font-size:11px;color:var(--text);}
.td-mono{font-size:9px;color:var(--dim);}
.td-ip{font-size:10px;color:var(--cyan);}
.td-payload{font-size:9px;color:var(--muted);max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}

.badge{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:2px;font-size:8px;letter-spacing:1px;border:1px solid;}
.b-sql{color:var(--red);border-color:rgba(255,0,64,0.3);background:rgba(255,0,64,0.06);}
.b-xss{color:var(--amber);border-color:rgba(255,170,0,0.3);background:rgba(255,170,0,0.06);}
.b-cmd{color:var(--cyan);border-color:rgba(0,255,255,0.3);background:rgba(0,255,255,0.06);}
.b-path{color:var(--orange);border-color:rgba(255,136,0,0.3);background:rgba(255,136,0,0.06);}
.b-honey{color:var(--amber);border-color:rgba(255,170,0,0.4);background:rgba(255,170,0,0.08);}
.b-brute{color:var(--violet);border-color:rgba(168,85,247,0.3);background:rgba(168,85,247,0.06);}
.b-csrf{color:#ff6b9d;border-color:rgba(255,107,157,0.3);background:rgba(255,107,157,0.06);}
.b-ssrf{color:#4fc3f7;border-color:rgba(79,195,247,0.3);background:rgba(79,195,247,0.06);}
.b-unk{color:var(--dim);border-color:var(--border);background:transparent;}
.b-block{color:var(--red);border-color:rgba(255,0,64,0.3);background:rgba(255,0,64,0.06);}

.sev-badge{display:inline-block;padding:2px 8px;border-radius:2px;font-size:7px;letter-spacing:2px;border:1px solid;}
.sev-CRITICAL{color:var(--red);border-color:rgba(255,0,64,0.4);background:rgba(255,0,64,0.08);}
.sev-HIGH{color:var(--amber);border-color:rgba(255,170,0,0.4);background:rgba(255,170,0,0.08);}
.sev-MEDIUM{color:var(--cyan);border-color:rgba(0,255,255,0.3);background:rgba(0,255,255,0.06);}
.sev-LOW{color:var(--g);border-color:rgba(0,255,65,0.3);background:rgba(0,255,65,0.06);}

.empty{text-align:center;padding:60px 40px;}
.empty-icon{font-size:40px;opacity:0.15;margin-bottom:14px;}
.empty-t{font-family:'Orbitron',monospace;font-size:13px;color:var(--g3);letter-spacing:2px;}

@media(max-width:900px){.stats{grid-template-columns:repeat(2,1fr);}.charts{grid-template-columns:1fr;}main{padding:24px;}}
</style>
</head>
<body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>

<nav>
  <div class="nav-left">
    <div class="logo">W-IPS</div>
    <div class="live-badge"><div class="live-dot"></div>LIVE MONITOR</div>
  </div>
  <div class="nav-links">
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:8080/login">DEMO</a>
    <a href="http://localhost:5003">REPORT</a>
    <button class="refresh-btn" onclick="location.reload()">&#8635; REFRESH</button>
  </div>
</nav>

<main>
  <div class="page-head">
    <h1>ATTACK MONITOR</h1>
    <p>REAL-TIME INTRUSION DETECTION &amp; PREVENTION LOG</p>
    <div class="time-info">&#8635; AUTO-REFRESH: 5s &nbsp;&middot;&nbsp; <span id="time"></span></div>
  </div>

  <!-- Stats -->
  <div class="stats">
    <div class="stat stat-r">
      <div class="stat-label">TOTAL ATTACKS</div>
      <div class="stat-num">{{ total }}</div>
      <div class="stat-sub">all detections</div>
    </div>
    <div class="stat stat-a">
      <div class="stat-label">SQL INJECTIONS</div>
      <div class="stat-num">{{ sql_count }}</div>
      <div class="stat-sub">database attacks</div>
    </div>
    <div class="stat stat-c">
      <div class="stat-label">XSS ATTACKS</div>
      <div class="stat-num">{{ xss_count }}</div>
      <div class="stat-sub">script injections</div>
    </div>
    <div class="stat stat-v">
      <div class="stat-label">HONEYPOTS HIT</div>
      <div class="stat-num">{{ honeypot_count }}</div>
      <div class="stat-sub">trap activations</div>
    </div>
    <div class="stat stat-g">
      <div class="stat-label">IPs BLOCKED</div>
      <div class="stat-num">{{ blocked_count }}</div>
      <div class="stat-sub">permanent bans</div>
    </div>
  </div>

  <!-- Severity -->
  <div class="sev-row">
    <div class="sev-card sev-critical">
      <div class="sev-icon">&#9888;</div>
      <div class="sev-info">
        <div class="sev-label">CRITICAL</div>
        <div class="sev-count">{{ sev_critical }}</div>
      </div>
    </div>
    <div class="sev-card sev-high">
      <div class="sev-icon">&#128308;</div>
      <div class="sev-info">
        <div class="sev-label">HIGH</div>
        <div class="sev-count">{{ sev_high }}</div>
      </div>
    </div>
    <div class="sev-card sev-medium">
      <div class="sev-icon">&#128993;</div>
      <div class="sev-info">
        <div class="sev-label">MEDIUM</div>
        <div class="sev-count">{{ sev_medium }}</div>
      </div>
    </div>
    <div class="sev-card sev-low">
      <div class="sev-icon">&#128994;</div>
      <div class="sev-info">
        <div class="sev-label">LOW</div>
        <div class="sev-count">{{ sev_low }}</div>
      </div>
    </div>
  </div>

  <!-- Charts -->
  <div class="charts">
    <div class="chart-card">
      <h3>ATTACK BREAKDOWN</h3>
      <p>DISTRIBUTION BY CATEGORY</p>
      <div class="chart-wrap"><canvas id="typeChart"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>TOP ATTACKER IPs</h3>
      <p>MOST FREQUENT SOURCES</p>
      <div class="chart-wrap"><canvas id="ipChart"></canvas></div>
    </div>
  </div>

  <!-- GeoIP -->
  <div class="geo-section">
    <div class="section-head">
      <h3>&#127760; ATTACK ORIGINS (GEOIP)</h3>
      <div class="log-count">{{ geo_data|length }} COUNTRIES</div>
    </div>
    {% if geo_data %}
    <div class="geo-grid">
      {% for country, count in geo_data %}
      <div class="geo-item">
        <div class="geo-flag">&#127760;</div>
        <div class="geo-info">
          <div class="geo-country">{{ country }}</div>
          <div class="geo-count">{{ count }} ATTACK{{ 'S' if count > 1 else '' }}</div>
        </div>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="empty"><div class="empty-icon">&#127760;</div><div class="empty-t">NO GEO DATA YET</div></div>
    {% endif %}
  </div>

  <!-- Honeypot hits -->
  <div class="honeypot-section">
    <div class="section-head hp-head">
      <h3>&#127855; HONEYPOT TRAP LOG</h3>
      <div class="log-count">{{ honeypot_count }} HITS</div>
    </div>
    {% if honeypot_logs %}
    <table>
      <thead><tr><th>#</th><th>TIMESTAMP</th><th>IP ADDRESS</th><th>TRAP PATH</th><th>ACTION</th></tr></thead>
      <tbody>
        {% for log in honeypot_logs|reverse %}
        <tr>
          <td class="td-mono">{{ loop.index }}</td>
          <td class="td-mono">{{ log.time }}</td>
          <td class="td-ip">{{ log.ip }}</td>
          <td class="td-payload">{{ log.payload }}</td>
          <td><span class="badge b-honey">HONEYPOT</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div class="empty"><div class="empty-icon">&#127855;</div><div class="empty-t">NO HONEYPOT TRIGGERS YET</div></div>
    {% endif %}
  </div>

  <!-- Attack log -->
  <div class="log-section">
    <div class="log-top">
      <h3>&#9889; FULL ATTACK LOG</h3>
      <div class="log-count">{{ total }} ENTRIES</div>
    </div>
    {% if logs %}
    <table>
      <thead>
        <tr><th>#</th><th>TIME</th><th>IP</th><th>COUNTRY</th><th>TYPE</th><th>SEVERITY</th><th>PAYLOAD</th><th>ACTION</th></tr>
      </thead>
      <tbody>
        {% for log in logs|reverse %}
        <tr>
          <td class="td-mono">{{ loop.index }}</td>
          <td class="td-mono">{{ log.time }}</td>
          <td class="td-ip">{{ log.ip }}</td>
          <td class="td-mono">{{ log.get('country','?') }}</td>
          <td>
            {% set t = log.get('attack_type','') %}
            {% if 'SQL' in t %}<span class="badge b-sql">SQL</span>
            {% elif 'XSS' in t %}<span class="badge b-xss">XSS</span>
            {% elif 'Command' in t %}<span class="badge b-cmd">CMD</span>
            {% elif 'Path' in t %}<span class="badge b-path">PATH</span>
            {% elif 'Honeypot' in t %}<span class="badge b-honey">HONEY</span>
            {% elif 'Brute' in t %}<span class="badge b-brute">BRUTE</span>
            {% elif 'CSRF' in t %}<span class="badge b-csrf">CSRF</span>
            {% elif 'SSRF' in t %}<span class="badge b-ssrf">SSRF</span>
            {% else %}<span class="badge b-unk">???</span>{% endif %}
          </td>
          <td>
            {% set s = log.get('severity','LOW') %}
            <span class="sev-badge sev-{{ s }}">{{ s }}</span>
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
      <div class="empty-t">NO THREATS DETECTED</div>
    </div>
    {% endif %}
  </div>
</main>

<script>
document.getElementById('time').textContent = new Date().toLocaleTimeString();
setTimeout(()=>location.reload(), 5000);

/* Matrix rain */
(function(){
  var cv=document.getElementById('matrix'),cx=cv.getContext('2d');
  var chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(){}[]<>/\\|;:!?~';
  var W,H,cols,drops;
  function init(){W=cv.width=innerWidth;H=cv.height=innerHeight;cols=Math.floor(W/16);drops=[];for(var i=0;i<cols;i++)drops[i]=Math.random()*-50;}
  init();window.addEventListener('resize',init);
  setInterval(function(){
    cx.fillStyle='rgba(5,10,5,0.05)';cx.fillRect(0,0,W,H);
    for(var i=0;i<drops.length;i++){
      var ch=chars[Math.floor(Math.random()*chars.length)],x=i*16,y=drops[i]*16;
      cx.fillStyle='#ccffcc';cx.font='bold 13px monospace';cx.fillText(ch,x,y);
      cx.fillStyle='#00ff41';cx.font='12px monospace';
      if(Math.random()>0.5&&y>16)cx.fillText(chars[Math.floor(Math.random()*chars.length)],x,y-16);
      if(y>H&&Math.random()>0.975)drops[i]=0;drops[i]++;
    }
  },45);
})();

Chart.defaults.color='rgba(0,255,65,0.4)';
Chart.defaults.borderColor='rgba(0,255,65,0.1)';
Chart.defaults.font.family="'Share Tech Mono',monospace";
Chart.defaults.font.size=10;

new Chart(document.getElementById('typeChart'),{
  type:'doughnut',
  data:{
    labels:['SQL','XSS','CMD','PATH','HONEYPOT','BRUTE FORCE','CSRF','SSRF','OTHER'],
    datasets:[{
      data:[{{sql_count}},{{xss_count}},{{cmd_count}},{{path_count}},{{honeypot_count}},{{brute_count}},{{csrf_count}},{{ssrf_count}},{{unknown_count}}],
      backgroundColor:['rgba(255,0,64,0.15)','rgba(255,170,0,0.15)','rgba(0,255,255,0.15)','rgba(255,136,0,0.15)','rgba(255,170,0,0.2)','rgba(168,85,247,0.15)','rgba(255,107,157,0.15)','rgba(79,195,247,0.15)','rgba(0,255,65,0.08)'],
      borderColor:['#ff0040','#ffaa00','#00ffff','#ff8800','#ffaa00','#a855f7','#ff6b9d','#4fc3f7','#00ff41'],
      borderWidth:1,
    }]
  },
  options:{responsive:true,maintainAspectRatio:false,cutout:'65%',
    plugins:{legend:{position:'right',labels:{padding:12,boxWidth:8,boxHeight:8,usePointStyle:true,color:'rgba(0,255,65,0.5)'}}}}
});

new Chart(document.getElementById('ipChart'),{
  type:'bar',
  data:{
    labels:{{ ip_labels | tojson }},
    datasets:[{label:'ATTACKS',data:{{ ip_counts | tojson }},
      backgroundColor:'rgba(0,255,65,0.08)',borderColor:'#00ff41',borderWidth:1,borderRadius:2}]
  },
  options:{responsive:true,maintainAspectRatio:false,
    plugins:{legend:{display:false}},
    scales:{
      x:{grid:{display:false},border:{display:false},ticks:{color:'rgba(0,255,65,0.4)'}},
      y:{beginAtZero:true,ticks:{stepSize:1,color:'rgba(0,255,65,0.4)'},grid:{color:'rgba(0,255,65,0.05)'},border:{display:false}}
    }
  }
});
</script>
</body>
</html>"""


def load_logs():
    logs = []
    try:
        with open('attacks.log', 'r') as f:
            for line in f:
                l = line.strip()
                if l:
                    try: logs.append(json.loads(l))
                    except: pass
    except: pass
    return logs

def get_blocked_count():
    try:
        with open('blocked_ips.json') as f:
            return len(json.load(f).get('blocked_ips', []))
    except: return 0

@app.route('/')
def dashboard():
    logs = load_logs()
    total = len(logs)

    sql_count     = sum(1 for l in logs if 'SQL'      in l.get('attack_type',''))
    xss_count     = sum(1 for l in logs if 'XSS'      in l.get('attack_type',''))
    cmd_count     = sum(1 for l in logs if 'Command'  in l.get('attack_type',''))
    path_count    = sum(1 for l in logs if 'Path'     in l.get('attack_type',''))
    honeypot_count= sum(1 for l in logs if 'Honeypot' in l.get('attack_type',''))
    brute_count   = sum(1 for l in logs if 'Brute'    in l.get('attack_type',''))
    csrf_count    = sum(1 for l in logs if 'CSRF'     in l.get('attack_type',''))
    ssrf_count    = sum(1 for l in logs if 'SSRF'     in l.get('attack_type',''))
    unknown_count = sum(1 for l in logs if not any(x in l.get('attack_type','')
        for x in ['SQL','XSS','Command','Path','Honeypot','Brute','CSRF','SSRF']))

    sev_critical = sum(1 for l in logs if l.get('severity') == 'CRITICAL')
    sev_high     = sum(1 for l in logs if l.get('severity') == 'HIGH')
    sev_medium   = sum(1 for l in logs if l.get('severity') == 'MEDIUM')
    sev_low      = sum(1 for l in logs if l.get('severity') == 'LOW')

    # GeoIP aggregation
    country_freq = {}
    for log in logs:
        c = log.get('country', 'Unknown')
        if c and c != 'Unknown':
            country_freq[c] = country_freq.get(c, 0) + 1
    geo_data = sorted(country_freq.items(), key=lambda x: x[1], reverse=True)[:12]

    # Honeypot logs
    honeypot_logs = [l for l in logs if 'Honeypot' in l.get('attack_type', '')]

    # Top IPs
    ip_freq = {}
    for log in logs:
        ip = log.get('ip', '?')
        ip_freq[ip] = ip_freq.get(ip, 0) + 1
    top = sorted(ip_freq.items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template_string(DASHBOARD,
        logs=logs, total=total,
        sql_count=sql_count, xss_count=xss_count, cmd_count=cmd_count,
        path_count=path_count, honeypot_count=honeypot_count,
        brute_count=brute_count, csrf_count=csrf_count,
        ssrf_count=ssrf_count, unknown_count=unknown_count,
        sev_critical=sev_critical, sev_high=sev_high,
        sev_medium=sev_medium, sev_low=sev_low,
        geo_data=geo_data, honeypot_logs=honeypot_logs,
        blocked_count=get_blocked_count(),
        ip_labels=[i for i,_ in top],
        ip_counts=[c for _,c in top],
    )

if __name__ == '__main__':
    app.run(port=5002, debug=False)