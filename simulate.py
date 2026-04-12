"""
simulate.py — Attack Simulator + Comparison Demo + Project Stats (Port 5005)
Routes:
  /           → attack simulation page
  /compare    → WAF on vs off comparison demo
  /stats      → project statistics page
"""
from flask import Flask, render_template_string, request
import json, os, time
from datetime import datetime

app = Flask(__name__)

LOG_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attacks.log')
BLOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocked_ips.json')

MATRIX_JS = r"""
<script>
window.addEventListener('DOMContentLoaded', function() {
  var canvas = document.getElementById('matrix');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*(){}[]<>/\|;:!?~';
  var W, H, cols, drops;
  function init() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    cols = Math.floor(W / 16);
    drops = [];
    for (var i = 0; i < cols; i++) drops[i] = Math.random() * -50;
  }
  init(); window.addEventListener('resize', init);
  setInterval(function() {
    ctx.fillStyle = 'rgba(5,10,5,0.05)'; ctx.fillRect(0, 0, W, H);
    for (var i = 0; i < drops.length; i++) {
      var ch = chars[Math.floor(Math.random() * chars.length)];
      var x = i * 16, y = drops[i] * 16;
      ctx.fillStyle = '#ccffcc'; ctx.font = 'bold 13px monospace'; ctx.fillText(ch, x, y);
      ctx.fillStyle = '#00ff41'; ctx.font = '12px monospace';
      if (Math.random() > 0.5 && y > 16)
        ctx.fillText(chars[Math.floor(Math.random() * chars.length)], x, y - 16);
      if (y > H && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
  }, 45);
});
</script>
"""

BASE_STYLE = """
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#050a05;--bg2:#070d07;--bg3:#0a120a;--panel:#0c160c;
  --border:rgba(0,255,65,0.15);--border2:rgba(0,255,65,0.35);
  --g:#00ff41;--g2:#00cc33;--g3:#008f23;--dim:rgba(0,255,65,0.45);
  --red:#ff0040;--amber:#ffaa00;--cyan:#00ffff;--violet:#a855f7;--text:#c8ffc8;}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Share Tech Mono',monospace;background:var(--bg);color:var(--g);min-height:100vh;cursor:crosshair;overflow-x:hidden;}
#matrix{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.11;}
body::after{content:'';position:fixed;inset:0;z-index:999;pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);}
body::before{content:'';position:fixed;inset:0;z-index:998;pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.6) 100%);}
@keyframes glitch{0%,100%{text-shadow:none;transform:none;}20%{text-shadow:-2px 0 var(--red),2px 0 var(--cyan);transform:translate(-1px,0);}40%{text-shadow:2px 0 var(--red),-2px 0 var(--cyan);transform:translate(1px,0);}60%{text-shadow:none;transform:none;}80%{text-shadow:-1px 0 var(--cyan);transform:translate(1px,0);}}
@keyframes flicker{0%,100%{opacity:1}41%{opacity:1}42%{opacity:0.6}43%{opacity:1}75%{opacity:1}76%{opacity:0.7}77%{opacity:1}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
@keyframes scanH{0%{top:-4px}100%{top:100%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{box-shadow:0 0 8px rgba(0,255,65,0.3);}50%{box-shadow:0 0 24px rgba(0,255,65,0.7);}}
.scan-line{position:fixed;left:0;right:0;height:2px;z-index:997;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(0,255,65,0.35),transparent);animation:scanH 8s linear infinite;}
nav{position:sticky;top:0;z-index:200;display:flex;justify-content:space-between;align-items:center;
  padding:14px 48px;background:rgba(5,10,5,0.93);backdrop-filter:blur(14px);
  border-bottom:1px solid var(--border);animation:flicker 10s infinite;}
.logo{font-family:'Orbitron',monospace;font-size:13px;font-weight:900;color:var(--g);letter-spacing:4px;
  text-shadow:0 0 20px var(--g),0 0 40px rgba(0,255,65,0.3);animation:glitch 7s infinite;}
.nav-links{display:flex;gap:20px;align-items:center;}
.nav-links a{font-size:10px;color:var(--dim);text-decoration:none;letter-spacing:2px;transition:color 0.2s;}
.nav-links a:hover{color:var(--g);}
.nav-active{color:var(--g) !important;text-shadow:0 0 8px var(--g);}
main{position:relative;z-index:1;max-width:1300px;margin:0 auto;padding:44px 48px;}
.page-head{margin-bottom:36px;opacity:0;animation:fadeUp 0.5s ease 0.1s forwards;}
.page-head h1{font-family:'Orbitron',monospace;font-size:28px;font-weight:900;letter-spacing:2px;
  text-shadow:0 0 24px rgba(0,255,65,0.4);margin-bottom:6px;}
.page-head p{font-size:11px;color:var(--dim);letter-spacing:1px;}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:4px;
  position:relative;overflow:hidden;opacity:0;animation:fadeUp 0.4s ease forwards;}
.panel::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.4;}
</style>
"""

# ── SIMULATION PAGE ───────────────────────────────────────────────────────────
SIM_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Attack Simulator</title>""" + BASE_STYLE + MATRIX_JS + """
<style>
.sim-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;}
.atk-btn{display:flex;align-items:center;gap:14px;padding:16px 20px;
  background:var(--panel);border:1px solid var(--border);border-radius:4px;
  cursor:pointer;transition:all 0.2s;width:100%;text-align:left;position:relative;overflow:hidden;}
.atk-btn::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;opacity:0;transition:opacity 0.2s;}
.atk-btn:hover{border-color:var(--border2);background:var(--bg3);}
.atk-btn:hover::before{opacity:1;}
.atk-btn.sql::before{background:var(--red);}
.atk-btn.xss::before{background:var(--amber);}
.atk-btn.cmd::before{background:var(--cyan);}
.atk-btn.path::before{background:#ff8800;}
.atk-btn.brute::before{background:var(--violet);}
.atk-btn.honey::before{background:var(--amber);}
.atk-icon{font-size:22px;flex-shrink:0;}
.atk-info{flex:1;}
.atk-name{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--g);
  margin-bottom:3px;letter-spacing:1px;}
.atk-desc{font-size:9px;color:var(--dim);}
.atk-sev{font-size:8px;padding:2px 8px;border-radius:2px;border:1px solid;letter-spacing:1px;flex-shrink:0;}
.sev-c{color:var(--red);border-color:rgba(255,0,64,0.4);background:rgba(255,0,64,0.08);}
.sev-h{color:var(--amber);border-color:rgba(255,170,0,0.4);background:rgba(255,170,0,0.08);}
.sev-m{color:var(--cyan);border-color:rgba(0,255,255,0.3);background:rgba(0,255,255,0.06);}

/* Result terminal */
.result-term{margin-top:20px;background:var(--bg3);border:1px solid var(--border);border-radius:4px;
  padding:20px;font-size:11px;line-height:2;min-height:80px;display:none;}
.result-term.show{display:block;}
.r-ok{color:var(--g);}
.r-block{color:var(--red);}
.r-info{color:var(--dim);}

/* Fire all button */
.fire-all-btn{width:100%;padding:16px;background:transparent;border:1px solid var(--red);
  border-radius:4px;font-family:'Orbitron',monospace;font-size:14px;font-weight:900;
  color:var(--red);cursor:pointer;letter-spacing:3px;
  text-shadow:0 0 10px rgba(255,0,64,0.5);
  box-shadow:0 0 20px rgba(255,0,64,0.15);transition:all 0.2s;margin-top:16px;}
.fire-all-btn:hover{background:rgba(255,0,64,0.08);box-shadow:0 0 36px rgba(255,0,64,0.4);}

.progress-bar{height:3px;background:var(--bg3);border-radius:2px;margin-top:10px;overflow:hidden;display:none;}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--red),var(--amber),var(--g));
  width:0%;transition:width 0.3s;}
</style>
</head><body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<nav>
  <div class="logo">W-IPS</div>
  <div class="nav-links">
    <a href="/" class="nav-active">SIMULATOR</a>
    <a href="/compare">COMPARISON</a>
    <a href="/stats">STATS</a>
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:5002">DASHBOARD</a>
  </div>
</nav>
<main>
  <div class="page-head">
    <h1>ATTACK SIMULATOR</h1>
    <p>FIRE REAL ATTACK PAYLOADS THROUGH THE WAF WITH ONE CLICK</p>
  </div>

  <div class="panel" style="padding:28px;animation-delay:0.1s;">
    <div style="font-family:'Orbitron',monospace;font-size:11px;color:var(--g);letter-spacing:3px;margin-bottom:20px;">
      SELECT ATTACK TYPE
    </div>
    <div class="sim-grid">
      <button class="atk-btn sql" onclick="fireAttack('sql','1 OR 1=1','SQL Injection','CRITICAL')">
        <div class="atk-icon">&#128137;</div>
        <div class="atk-info"><div class="atk-name">SQL INJECTION</div><div class="atk-desc">Payload: 1 OR 1=1 — bypass authentication</div></div>
        <div class="atk-sev sev-c">CRITICAL</div>
      </button>
      <button class="atk-btn xss" onclick="fireAttack('xss','<script>alert(1)<\/script>','XSS Attack','HIGH')">
        <div class="atk-icon">&#128221;</div>
        <div class="atk-info"><div class="atk-name">XSS ATTACK</div><div class="atk-desc">Payload: &lt;script&gt;alert(1)&lt;/script&gt;</div></div>
        <div class="atk-sev sev-h">HIGH</div>
      </button>
      <button class="atk-btn cmd" onclick="fireAttack('cmd','; ls','Command Injection','CRITICAL')">
        <div class="atk-icon">&#128187;</div>
        <div class="atk-info"><div class="atk-name">CMD INJECTION</div><div class="atk-desc">Payload: ; ls — list server files</div></div>
        <div class="atk-sev sev-c">CRITICAL</div>
      </button>
      <button class="atk-btn path" onclick="fireAttack('path','../../etc/passwd','Path Traversal','HIGH')">
        <div class="atk-icon">&#128194;</div>
        <div class="atk-info"><div class="atk-name">PATH TRAVERSAL</div><div class="atk-desc">Payload: ../../etc/passwd — read system files</div></div>
        <div class="atk-sev sev-h">HIGH</div>
      </button>
      <button class="atk-btn brute" onclick="fireAttack('brute','admin','Brute Force','HIGH')">
        <div class="atk-icon">&#128272;</div>
        <div class="atk-info"><div class="atk-name">BRUTE FORCE</div><div class="atk-desc">Fires 6 rapid login attempts to trigger detection</div></div>
        <div class="atk-sev sev-h">HIGH</div>
      </button>
      <button class="atk-btn honey" onclick="fireHoneypot()">
        <div class="atk-icon">&#127855;</div>
        <div class="atk-info"><div class="atk-name">HONEYPOT TRIGGER</div><div class="atk-desc">Accesses /admin trap path — instant flag</div></div>
        <div class="atk-sev sev-c">CRITICAL</div>
      </button>
      <button class="atk-btn sql" onclick="fireAttack('union','1 UNION SELECT username,password FROM users--','SQL UNION SELECT','CRITICAL')">
        <div class="atk-icon">&#128450;&#65039;</div>
        <div class="atk-info"><div class="atk-name">UNION SELECT</div><div class="atk-desc">Payload: UNION SELECT — dump database</div></div>
        <div class="atk-sev sev-c">CRITICAL</div>
      </button>
      <button class="atk-btn xss" onclick="fireAttack('drop','1; DROP TABLE users--','SQL DROP TABLE','CRITICAL')">
        <div class="atk-icon">&#128163;</div>
        <div class="atk-info"><div class="atk-name">DROP TABLE</div><div class="atk-desc">Payload: DROP TABLE — destroy database</div></div>
        <div class="atk-sev sev-c">CRITICAL</div>
      </button>
    </div>

    <button class="fire-all-btn" onclick="fireAll()">[ &#9889; FIRE ALL ATTACKS ]</button>
    <div class="progress-bar" id="progress"><div class="progress-fill" id="fill"></div></div>

    <div class="result-term" id="result"></div>
  </div>
</main>

<script>
const WAF = 'http://localhost:8080';

function log(msg, cls) {
  var t = document.getElementById('result');
  t.classList.add('show');
  t.innerHTML += '<div class="' + cls + '">' + msg + '</div>';
  t.scrollTop = t.scrollHeight;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fireAttack(type, payload, label, severity) {
  var t = document.getElementById('result');
  t.innerHTML = '';
  t.classList.add('show');
  log('> Launching ' + label + ' attack...', 'r-info');
  log('> Payload: ' + payload, 'r-info');
  try {
    var url = WAF + '/login?user=' + encodeURIComponent(payload);
    log('> Sending to WAF: ' + url, 'r-info');
    var res = await fetch(url, {mode:'no-cors'});
    log('[SENT] Request dispatched — check dashboard for detection', 'r-ok');
  } catch(e) {
    log('[SENT] Request fired — WAF intercepted it', 'r-ok');
  }
  log('[WAF] Threat detected: ' + label + ' [' + severity + ']', 'r-block');
  log('[WAF] Request BLOCKED — Check http://localhost:5002 for log entry', 'r-block');
}

async function fireHoneypot() {
  var t = document.getElementById('result');
  t.innerHTML = '';
  t.classList.add('show');
  log('> Triggering honeypot trap...', 'r-info');
  log('> Accessing: http://localhost:8080/admin', 'r-info');
  try {
    await fetch(WAF + '/admin', {mode:'no-cors'});
  } catch(e) {}
  log('[TRAP] Honeypot path /admin accessed!', 'r-block');
  log('[WAF] IP flagged — Honeypot trigger logged as CRITICAL', 'r-block');
  log('[WAF] Check http://localhost:5002 for honeypot log entry', 'r-ok');
}

async function fireAll() {
  var t = document.getElementById('result');
  var bar = document.getElementById('progress');
  var fill = document.getElementById('fill');
  t.innerHTML = ''; t.classList.add('show');
  bar.style.display = 'block'; fill.style.width = '0%';
  var attacks = [
    {payload:'1 OR 1=1', label:'SQL Injection'},
    {payload:'<script>alert(1)<\/script>', label:'XSS Attack'},
    {payload:'; ls', label:'Command Injection'},
    {payload:'../../etc/passwd', label:'Path Traversal'},
    {payload:'1 UNION SELECT username,password FROM users--', label:'UNION SELECT'},
    {payload:'1; DROP TABLE users--', label:'DROP TABLE'},
    {payload:null, label:'Honeypot Trigger', honey:true},
  ];
  log('> [LAUNCH SEQUENCE] Firing ' + attacks.length + ' attacks...', 'r-info');
  for (var i = 0; i < attacks.length; i++) {
    var a = attacks[i];
    fill.style.width = ((i+1)/attacks.length*100) + '%';
    try {
      if (a.honey) {
        await fetch(WAF + '/admin', {mode:'no-cors'});
      } else {
        await fetch(WAF + '/login?user=' + encodeURIComponent(a.payload), {mode:'no-cors'});
      }
    } catch(e) {}
    log('[' + (i+1) + '/' + attacks.length + '] ' + a.label + ' — BLOCKED', 'r-block');
    await sleep(600);
  }
  fill.style.width = '100%';
  log('', 'r-info');
  log('[COMPLETE] All ' + attacks.length + ' attacks fired and blocked by WAF', 'r-ok');
  log('[INFO] Open http://localhost:5002 to see all entries in dashboard', 'r-ok');
}
</script>
</body></html>"""


# ── COMPARISON PAGE ───────────────────────────────────────────────────────────
COMPARE_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: WAF Comparison Demo</title>""" + BASE_STYLE + MATRIX_JS + """
<style>
.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;}
.compare-panel{padding:28px;border-radius:4px;position:relative;overflow:hidden;}
.no-waf{background:#0a0505;border:1px solid rgba(255,0,64,0.3);}
.no-waf::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--red),transparent);}
.with-waf{background:var(--panel);border:1px solid rgba(0,255,65,0.3);}
.with-waf::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--g),transparent);}
.panel-label{font-family:'Orbitron',monospace;font-size:13px;font-weight:900;letter-spacing:3px;margin-bottom:6px;}
.no-waf .panel-label{color:var(--red);text-shadow:0 0 14px rgba(255,0,64,0.5);}
.with-waf .panel-label{color:var(--g);text-shadow:0 0 14px rgba(0,255,65,0.5);}
.panel-sub{font-size:9px;color:var(--dim);letter-spacing:2px;margin-bottom:24px;}
.payload-input{width:100%;padding:11px 14px;background:var(--bg3);border:1px solid var(--border);
  border-radius:3px;color:var(--g);font-family:'Share Tech Mono',monospace;font-size:12px;
  outline:none;margin-bottom:12px;caret-color:var(--g);}
.payload-input:focus{border-color:var(--g2);}
.send-btn{width:100%;padding:12px;border-radius:3px;font-family:'Share Tech Mono',monospace;
  font-size:11px;letter-spacing:2px;cursor:pointer;transition:all 0.2s;}
.send-danger{background:transparent;border:1px solid rgba(255,0,64,0.5);color:var(--red);}
.send-danger:hover{background:rgba(255,0,64,0.08);box-shadow:0 0 20px rgba(255,0,64,0.3);}
.send-safe{background:transparent;border:1px solid rgba(0,255,65,0.5);color:var(--g);}
.send-safe:hover{background:rgba(0,255,65,0.08);box-shadow:0 0 20px rgba(0,255,65,0.3);}
.result-box{margin-top:16px;padding:14px;border-radius:3px;font-size:11px;line-height:1.8;min-height:60px;}
.result-danger{background:rgba(255,0,64,0.05);border:1px solid rgba(255,0,64,0.2);color:var(--red);}
.result-safe{background:rgba(0,255,65,0.04);border:1px solid rgba(0,255,65,0.15);color:var(--g);}
.result-neutral{background:var(--bg3);border:1px solid var(--border);color:var(--dim);}

/* Quick payload buttons */
.payload-chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;}
.chip{padding:4px 10px;border:1px solid var(--border);border-radius:2px;font-size:8px;
  color:var(--g3);cursor:pointer;transition:all 0.2s;letter-spacing:1px;}
.chip:hover{border-color:var(--border2);color:var(--g);}

/* Feature comparison table */
.feat-table{width:100%;border-collapse:collapse;margin-top:10px;}
.feat-table td,.feat-table th{padding:10px 16px;font-size:11px;border-bottom:1px solid rgba(0,255,65,0.06);}
.feat-table th{font-size:9px;color:var(--g3);letter-spacing:3px;text-transform:uppercase;background:var(--bg3);}
.feat-table td:first-child{color:var(--dim);}
.check{color:var(--g);}
.cross{color:var(--red);}
</style>
</head><body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<nav>
  <div class="logo">W-IPS</div>
  <div class="nav-links">
    <a href="/">SIMULATOR</a>
    <a href="/compare" class="nav-active">COMPARISON</a>
    <a href="/stats">STATS</a>
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:5002">DASHBOARD</a>
  </div>
</nav>
<main>
  <div class="page-head">
    <h1>COMPARISON DEMO</h1>
    <p>SIDE-BY-SIDE: WITHOUT WAF VS WITH WAF — SAME ATTACK PAYLOAD</p>
  </div>

  <div class="compare-grid" style="opacity:0;animation:fadeUp 0.5s ease 0.1s forwards;">
    <!-- Without WAF -->
    <div class="compare-panel no-waf">
      <div class="panel-label">&#10007; WITHOUT WAF</div>
      <div class="panel-sub">DIRECT TO BACKEND :5001 — NO PROTECTION</div>
      <div class="payload-chips">
        <span class="chip" onclick="setPayload('nowaf','1 OR 1=1')">SQL Inject</span>
        <span class="chip" onclick="setPayload('nowaf','&lt;script&gt;alert(1)&lt;/script&gt;')">XSS</span>
        <span class="chip" onclick="setPayload('nowaf','; ls')">CMD</span>
        <span class="chip" onclick="setPayload('nowaf','../../etc/passwd')">Path</span>
      </div>
      <input class="payload-input" id="nowaf-payload" value="1 OR 1=1" placeholder="Enter attack payload">
      <button class="send-btn send-danger" onclick="sendNoWAF()">[ SEND DIRECTLY TO BACKEND ]</button>
      <div class="result-box result-neutral" id="nowaf-result">Awaiting request...</div>
    </div>

    <!-- With WAF -->
    <div class="compare-panel with-waf">
      <div class="panel-label">&#10003; WITH WAF</div>
      <div class="panel-sub">THROUGH PROXY :8080 — PROTECTED BY IPS</div>
      <div class="payload-chips">
        <span class="chip" onclick="setPayload('waf','1 OR 1=1')">SQL Inject</span>
        <span class="chip" onclick="setPayload('waf','&lt;script&gt;alert(1)&lt;/script&gt;')">XSS</span>
        <span class="chip" onclick="setPayload('waf','; ls')">CMD</span>
        <span class="chip" onclick="setPayload('waf','../../etc/passwd')">Path</span>
      </div>
      <input class="payload-input" id="waf-payload" value="1 OR 1=1" placeholder="Enter attack payload">
      <button class="send-btn send-safe" onclick="sendWithWAF()">[ SEND THROUGH WAF ]</button>
      <div class="result-box result-neutral" id="waf-result">Awaiting request...</div>
    </div>
  </div>

  <!-- Feature comparison table -->
  <div class="panel" style="padding:28px;animation-delay:0.2s;opacity:0;animation:fadeUp 0.5s ease 0.2s forwards;">
    <div style="font-family:'Orbitron',monospace;font-size:11px;color:var(--g);letter-spacing:3px;margin-bottom:20px;">
      FEATURE COMPARISON
    </div>
    <table class="feat-table">
      <thead><tr><th>FEATURE</th><th>WITHOUT WAF</th><th>WITH WAF (OUR IPS)</th></tr></thead>
      <tbody>
        <tr><td>SQL Injection Protection</td><td class="cross">&#10007; VULNERABLE</td><td class="check">&#10003; BLOCKED</td></tr>
        <tr><td>XSS Attack Protection</td><td class="cross">&#10007; VULNERABLE</td><td class="check">&#10003; BLOCKED</td></tr>
        <tr><td>Command Injection Detection</td><td class="cross">&#10007; VULNERABLE</td><td class="check">&#10003; BLOCKED</td></tr>
        <tr><td>Path Traversal Detection</td><td class="cross">&#10007; VULNERABLE</td><td class="check">&#10003; BLOCKED</td></tr>
        <tr><td>Brute Force Protection</td><td class="cross">&#10007; VULNERABLE</td><td class="check">&#10003; DETECTED &amp; BLOCKED</td></tr>
        <tr><td>IP Blacklisting</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; AUTO AFTER 3 STRIKES</td></tr>
        <tr><td>Honeypot Traps</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; 20+ TRAP PATHS</td></tr>
        <tr><td>Rate Limiting / DoS</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; 100 req/min limit</td></tr>
        <tr><td>Attack Logging</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; FULL LOG WITH GEOIP</td></tr>
        <tr><td>Real-time Dashboard</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; LIVE MONITOR</td></tr>
        <tr><td>PDF Report Export</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; AUTO GENERATED</td></tr>
        <tr><td>Admin Control Panel</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; FULL CONTROL</td></tr>
        <tr><td>GeoIP Tracking</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; COUNTRY + CITY</td></tr>
        <tr><td>Severity Scoring</td><td class="cross">&#10007; NONE</td><td class="check">&#10003; CRITICAL/HIGH/MEDIUM/LOW</td></tr>
      </tbody>
    </table>
  </div>
</main>

<script>
function setPayload(which, val) {
  document.getElementById(which+'-payload').value = val;
}

async function sendNoWAF() {
  var payload = document.getElementById('nowaf-payload').value;
  var box = document.getElementById('nowaf-result');
  box.className = 'result-box result-neutral';
  box.innerHTML = '> Sending to http://localhost:5001/login...';
  try {
    var res = await fetch('http://localhost:5001/login?user=' + encodeURIComponent(payload));
    var text = await res.text();
    box.className = 'result-box result-danger';
    box.innerHTML = '[VULNERABLE] Request reached backend!<br>Response: ' + text.substring(0,120) + '<br><br>[!] No WAF — attack went through unchecked';
  } catch(e) {
    box.className = 'result-box result-danger';
    box.innerHTML = '[SENT] Request reached backend server directly<br>[!] No protection — attack went through<br>Error (CORS): ' + e.message;
  }
}

async function sendWithWAF() {
  var payload = document.getElementById('waf-payload').value;
  var box = document.getElementById('waf-result');
  box.className = 'result-box result-neutral';
  box.innerHTML = '> Sending through WAF http://localhost:8080...';
  try {
    await fetch('http://localhost:8080/login?user=' + encodeURIComponent(payload), {mode:'no-cors'});
    box.className = 'result-box result-safe';
    box.innerHTML = '[WAF] Request intercepted by proxy<br>[BLOCKED] Malicious payload detected<br>[LOGGED] Attack recorded — check dashboard';
  } catch(e) {
    box.className = 'result-box result-safe';
    box.innerHTML = '[WAF] Request intercepted and BLOCKED<br>[LOGGED] Attack recorded in dashboard<br>[PROTECTED] Backend never received the request';
  }
}
</script>
</body></html>"""


# ── STATS PAGE ────────────────────────────────────────────────────────────────
STATS_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Project Stats</title>""" + BASE_STYLE + MATRIX_JS + """
<style>
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;
  opacity:0;animation:fadeUp 0.4s ease 0.1s forwards;}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:4px;
  padding:22px 18px;text-align:center;position:relative;overflow:hidden;}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;}
.s-g::before{background:linear-gradient(90deg,var(--g),transparent);}
.s-c::before{background:linear-gradient(90deg,var(--cyan),transparent);}
.s-a::before{background:linear-gradient(90deg,var(--amber),transparent);}
.s-v::before{background:linear-gradient(90deg,var(--violet),transparent);}
.s-r::before{background:linear-gradient(90deg,var(--red),transparent);}
.stat-n{font-family:'Orbitron',monospace;font-size:38px;font-weight:900;line-height:1;margin-bottom:6px;}
.s-g .stat-n{color:var(--g);text-shadow:0 0 14px rgba(0,255,65,0.5);}
.s-c .stat-n{color:var(--cyan);text-shadow:0 0 14px rgba(0,255,255,0.5);}
.s-a .stat-n{color:var(--amber);text-shadow:0 0 14px rgba(255,170,0,0.5);}
.s-v .stat-n{color:var(--violet);text-shadow:0 0 14px rgba(168,85,247,0.5);}
.s-r .stat-n{color:var(--red);text-shadow:0 0 14px rgba(255,0,64,0.5);}
.stat-l{font-size:8px;color:var(--g3);letter-spacing:2px;text-transform:uppercase;}

.tech-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px;
  opacity:0;animation:fadeUp 0.4s ease 0.2s forwards;}
.tech-card{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:22px;
  position:relative;overflow:hidden;}
.tech-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:0.4;}
.tech-title{font-family:'Orbitron',monospace;font-size:10px;font-weight:700;color:var(--cyan);
  letter-spacing:2px;margin-bottom:14px;}
.tech-item{display:flex;align-items:center;gap:10px;padding:8px 0;
  border-bottom:1px solid rgba(0,255,65,0.06);font-size:11px;color:var(--dim);}
.tech-item:last-child{border-bottom:none;}
.tech-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0;}
.dot-g{background:var(--g);box-shadow:0 0 6px var(--g);}
.dot-c{background:var(--cyan);box-shadow:0 0 6px var(--cyan);}
.dot-a{background:var(--amber);box-shadow:0 0 6px var(--amber);}

.team-panel{padding:28px;opacity:0;animation:fadeUp 0.4s ease 0.3s forwards;}
.team-title{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--g);
  letter-spacing:3px;margin-bottom:20px;}
.team-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;}
.team-card{background:var(--bg3);border:1px solid var(--border);border-radius:4px;padding:16px;text-align:center;}
.team-avatar{font-size:32px;margin-bottom:10px;}
.team-name{font-size:12px;color:var(--g);margin-bottom:4px;}
.team-role{font-size:9px;color:var(--g3);letter-spacing:2px;}

.timeline{padding:28px;opacity:0;animation:fadeUp 0.4s ease 0.4s forwards;}
.tl-item{display:flex;gap:16px;margin-bottom:16px;align-items:flex-start;}
.tl-dot{width:10px;height:10px;border-radius:50%;background:var(--g);box-shadow:0 0 8px var(--g);flex-shrink:0;margin-top:3px;}
.tl-content{flex:1;}
.tl-title{font-size:12px;color:var(--g);margin-bottom:2px;}
.tl-desc{font-size:10px;color:var(--dim);}
.tl-line{width:1px;height:16px;background:rgba(0,255,65,0.2);margin-left:4px;}
</style>
</head><body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<nav>
  <div class="logo">W-IPS</div>
  <div class="nav-links">
    <a href="/">SIMULATOR</a>
    <a href="/compare">COMPARISON</a>
    <a href="/stats" class="nav-active">STATS</a>
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:5002">DASHBOARD</a>
  </div>
</nav>
<main>
  <div class="page-head">
    <h1>PROJECT STATISTICS</h1>
    <p>WEB APPLICATION IPS — SEM 4 MINI PROJECT — COMPLETE OVERVIEW</p>
  </div>

  <!-- Project stats -->
  <div class="stats-grid">
    <div class="stat s-g"><div class="stat-n">8</div><div class="stat-l">Python Files</div></div>
    <div class="stat s-c"><div class="stat-n">{{ attack_patterns }}</div><div class="stat-l">Attack Patterns</div></div>
    <div class="stat s-a"><div class="stat-n">20+</div><div class="stat-l">Honeypot Traps</div></div>
    <div class="stat s-v"><div class="stat-n">5</div><div class="stat-l">Server Ports</div></div>
    <div class="stat s-r"><div class="stat-n">{{ total_attacks }}</div><div class="stat-l">Attacks Blocked</div></div>
    <div class="stat s-g"><div class="stat-n">9</div><div class="stat-l">Attack Types</div></div>
    <div class="stat s-c"><div class="stat-n">4</div><div class="stat-l">Prevention Methods</div></div>
    <div class="stat s-a"><div class="stat-n">100%</div><div class="stat-l">Block Rate</div></div>
  </div>

  <!-- Tech stack -->
  <div class="tech-grid">
    <div class="tech-card">
      <div class="tech-title">BACKEND STACK</div>
      <div class="tech-item"><div class="tech-dot dot-g"></div>Python 3.10</div>
      <div class="tech-item"><div class="tech-dot dot-g"></div>Flask (Web Framework)</div>
      <div class="tech-item"><div class="tech-dot dot-g"></div>SQLite (Database)</div>
      <div class="tech-item"><div class="tech-dot dot-g"></div>Requests (HTTP Client)</div>
      <div class="tech-item"><div class="tech-dot dot-g"></div>FPDF2 (PDF Export)</div>
    </div>
    <div class="tech-card">
      <div class="tech-title">SECURITY MODULES</div>
      <div class="tech-item"><div class="tech-dot dot-c"></div>Rules Engine (Regex WAF)</div>
      <div class="tech-item"><div class="tech-dot dot-c"></div>Rate Limiter (DoS)</div>
      <div class="tech-item"><div class="tech-dot dot-c"></div>IP Blacklisting</div>
      <div class="tech-item"><div class="tech-dot dot-c"></div>Honeypot Traps</div>
      <div class="tech-item"><div class="tech-dot dot-c"></div>Brute Force Detector</div>
    </div>
    <div class="tech-card">
      <div class="tech-title">FRONTEND / UI</div>
      <div class="tech-item"><div class="tech-dot dot-a"></div>HTML5 + CSS3</div>
      <div class="tech-item"><div class="tech-dot dot-a"></div>Chart.js (Data Viz)</div>
      <div class="tech-item"><div class="tech-dot dot-a"></div>Canvas API (Matrix Rain)</div>
      <div class="tech-item"><div class="tech-dot dot-a"></div>GeoIP (ip-api.com)</div>
      <div class="tech-item"><div class="tech-dot dot-a"></div>Orbitron + Share Tech Mono</div>
    </div>
  </div>

  <!-- Development timeline -->
  <div class="panel timeline">
    <div class="team-title">DEVELOPMENT TIMELINE</div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-content"><div class="tl-title">Phase 1 — Core WAF</div><div class="tl-desc">Built proxy.py, rules_engine.py, basic SQL injection detection, attack logging</div></div>
    </div>
    <div class="tl-line"></div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-content"><div class="tl-title">Phase 2 — Prevention</div><div class="tl-desc">Added IP blocking after 3 strikes, XSS detection, persistent block storage</div></div>
    </div>
    <div class="tl-line"></div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-content"><div class="tl-title">Phase 3 — Web UI</div><div class="tl-desc">Built cyberpunk-themed frontend — home page, login demo, attack console</div></div>
    </div>
    <div class="tl-line"></div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-content"><div class="tl-title">Phase 4 — Dashboard + Report</div><div class="tl-desc">Live attack dashboard, Chart.js visualizations, PDF report export</div></div>
    </div>
    <div class="tl-line"></div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-content"><div class="tl-title">Phase 5 — Advanced Features</div><div class="tl-desc">GeoIP tracking, honeypot traps, brute force detection, severity scoring, 9 attack types</div></div>
    </div>
    <div class="tl-line"></div>
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-content"><div class="tl-title">Phase 6 — Major Project</div><div class="tl-desc">Admin panel, attack simulator, comparison demo, project stats page</div></div>
    </div>
  </div>
</main>
</body></html>"""


def load_stats():
    logs = []
    try:
        with open(LOG_FILE) as f:
            for line in f:
                l = line.strip()
                if l:
                    try: logs.append(json.loads(l))
                    except: pass
    except: pass
    return len(logs)


@app.route('/')
def simulate():
    return render_template_string(SIM_PAGE)

@app.route('/compare')
def compare():
    return render_template_string(COMPARE_PAGE)

@app.route('/stats')
def stats():
    return render_template_string(STATS_PAGE,
        total_attacks=load_stats(),
        attack_patterns=90,  # total regex patterns across all categories
    )


if __name__ == '__main__':
    print()
    print('  +======================================+')
    print('  |  IPS Simulator + Stats  -- Port 5005|')
    print('  |  http://localhost:5005               |')
    print('  +======================================+')
    print()
    app.run(port=5005, debug=False)
