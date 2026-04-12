from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

SHARED_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root {
  --bg:#050a05; --bg2:#070d07; --bg3:#0a120a; --panel:#0c160c;
  --border:rgba(0,255,65,0.15); --border2:rgba(0,255,65,0.35);
  --g:#00ff41; --g2:#00cc33; --g3:#008f23;
  --dim:rgba(0,255,65,0.45); --muted:rgba(0,255,65,0.3);
  --red:#ff0040; --amber:#ffaa00; --cyan:#00ffff; --text:#c8ffc8;
}
*,*::before,*::after { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
  font-family:'Share Tech Mono',monospace;
  background:var(--bg); color:var(--g);
  min-height:100vh; cursor:crosshair; overflow-x:hidden;
}
#matrix { position:fixed; inset:0; z-index:0; pointer-events:none; opacity:0.13; }
body::after {
  content:''; position:fixed; inset:0; z-index:999; pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);
}
body::before {
  content:''; position:fixed; inset:0; z-index:998; pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.6) 100%);
}
@keyframes glitch {
  0%,100%{text-shadow:none;transform:none;}
  20%{text-shadow:-2px 0 var(--red),2px 0 var(--cyan);transform:translate(-1px,0);}
  40%{text-shadow:2px 0 var(--red),-2px 0 var(--cyan);transform:translate(1px,0);}
  60%{text-shadow:none;transform:none;}
  80%{text-shadow:-1px 0 var(--cyan);transform:translate(1px,0);}
}
@keyframes flicker {
  0%,100%{opacity:1} 41%{opacity:1} 42%{opacity:0.6} 43%{opacity:1}
  75%{opacity:1} 76%{opacity:0.7} 77%{opacity:1}
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes scanH { 0%{top:-4px} 100%{top:100%} }
@keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes glow-pulse {
  0%,100%{box-shadow:0 0 8px rgba(0,255,65,0.3),inset 0 0 8px rgba(0,255,65,0.05);}
  50%{box-shadow:0 0 20px rgba(0,255,65,0.6),inset 0 0 16px rgba(0,255,65,0.1);}
}
@keyframes border-run {
  0%   { background-position: 0% 50%; }
  100% { background-position: 300% 50%; }
}

.scan-line {
  position:fixed; left:0; right:0; height:3px; z-index:997; pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(0,255,65,0.4),transparent);
  animation:scanH 8s linear infinite;
}
nav {
  position:fixed; top:0; left:0; right:0; z-index:200;
  display:flex; justify-content:space-between; align-items:center;
  padding:14px 48px;
  background:rgba(5,10,5,0.92); backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  animation:flicker 8s infinite;
}
.logo {
  font-family:'Orbitron',monospace; font-size:15px; font-weight:900;
  color:var(--g); letter-spacing:4px;
  text-shadow:0 0 20px var(--g),0 0 40px rgba(0,255,65,0.3);
  animation:glitch 6s infinite;
}
.nav-status { display:flex; align-items:center; gap:8px; font-size:11px; color:var(--dim); letter-spacing:2px; }
.status-dot {
  width:7px; height:7px; border-radius:50%; background:var(--g);
  box-shadow:0 0 8px var(--g); animation:blink 1.2s ease-in-out infinite;
}
.nav-links { display:flex; gap:28px; align-items:center; }
.nav-links a {
  font-size:11px; color:var(--dim); text-decoration:none; letter-spacing:2px;
  transition:color 0.2s,text-shadow 0.2s;
}
.nav-links a:hover { color:var(--g); text-shadow:0 0 10px var(--g); }
.nav-report-btn {
  font-size:10px; color:var(--amber); text-decoration:none; letter-spacing:2px;
  border:1px solid rgba(255,170,0,0.4); padding:5px 14px; border-radius:3px;
  transition:all 0.2s;
  text-shadow:0 0 8px rgba(255,170,0,0.5);
  box-shadow:0 0 10px rgba(255,170,0,0.1);
}
.nav-report-btn:hover {
  background:rgba(255,170,0,0.08);
  border-color:var(--amber);
  box-shadow:0 0 20px rgba(255,170,0,0.3);
  color:var(--amber) !important;
  text-shadow:0 0 12px var(--amber) !important;
}

.btn {
  display:inline-flex; align-items:center; gap:8px; padding:12px 28px;
  font-family:'Share Tech Mono',monospace; font-size:13px; letter-spacing:2px;
  text-decoration:none; cursor:pointer; border-radius:3px; transition:all 0.2s;
}
.btn-primary {
  background:transparent; border:1px solid var(--g); color:var(--g);
  text-shadow:0 0 8px var(--g);
  box-shadow:0 0 12px rgba(0,255,65,0.2),inset 0 0 12px rgba(0,255,65,0.05);
}
.btn-primary:hover {
  background:rgba(0,255,65,0.08);
  box-shadow:0 0 24px rgba(0,255,65,0.5),inset 0 0 20px rgba(0,255,65,0.1);
  transform:translateY(-2px);
}
.btn-ghost { background:transparent; border:1px solid var(--border2); color:var(--dim); }
.btn-ghost:hover { border-color:var(--g); color:var(--g); box-shadow:0 0 12px rgba(0,255,65,0.2); }
.btn-amber {
  background:transparent; border:1px solid rgba(255,170,0,0.4); color:var(--amber);
  text-shadow:0 0 8px rgba(255,170,0,0.5);
  box-shadow:0 0 12px rgba(255,170,0,0.1);
}
.btn-amber:hover {
  background:rgba(255,170,0,0.08);
  box-shadow:0 0 24px rgba(255,170,0,0.4);
  transform:translateY(-2px);
}

input[type=text],input[type=password] {
  width:100%; padding:13px 16px; background:var(--bg3);
  border:1px solid var(--border); border-radius:3px;
  color:var(--g); font-family:'Share Tech Mono',monospace; font-size:13px;
  outline:none; transition:border-color 0.2s,box-shadow 0.2s; caret-color:var(--g);
}
input:focus { border-color:var(--g2); box-shadow:0 0 16px rgba(0,255,65,0.2); }
input::placeholder { color:var(--muted); }
label { display:block; font-size:9px; color:var(--g3); letter-spacing:3px; text-transform:uppercase; margin-bottom:8px; }
</style>
"""

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

HOME_PAGE = ("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Intrusion Prevention System</title>
""" + SHARED_CSS + MATRIX_JS + """
<style>
.hero {
  position:relative; z-index:1;
  min-height:100vh;
  display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; padding:120px 40px 80px;
}
.terminal-box {
  margin:0 auto 40px; max-width:460px; text-align:left;
  border:1px solid var(--border); border-radius:4px; overflow:hidden;
  opacity:0; animation:fadeUp 0.5s ease 0.2s forwards;
}
.term-bar {
  background:var(--bg3); padding:8px 16px;
  display:flex; align-items:center; gap:8px; border-bottom:1px solid var(--border);
}
.term-dot { width:10px; height:10px; border-radius:50%; }
.term-title { font-size:10px; color:var(--g3); letter-spacing:2px; flex:1; text-align:center; }
.term-body { padding:16px 20px; font-size:11px; line-height:2.2; }
.term-line { display:flex; gap:8px; }
.term-prompt { color:var(--g2); flex-shrink:0; }
.term-out { color:var(--dim); padding-left:16px; }
.term-ok { color:var(--g); }
.term-warn { color:var(--amber); }
.term-cursor {
  display:inline-block; width:8px; height:14px; background:var(--g);
  animation:blink 1s step-end infinite; vertical-align:text-bottom;
}
.hero-title {
  font-family:'Orbitron',monospace;
  font-size:clamp(36px,7vw,88px); font-weight:900; line-height:1;
  text-shadow:0 0 30px rgba(0,255,65,0.5),0 0 60px rgba(0,255,65,0.2);
  animation:glitch 5s infinite, fadeUp 0.7s ease 0.5s both;
  margin-bottom:8px;
}
.hero-sub {
  font-family:'Orbitron',monospace;
  font-size:clamp(12px,2vw,20px); font-weight:400;
  color:var(--dim); letter-spacing:8px;
  animation:fadeUp 0.7s ease 0.7s both; margin-bottom:24px;
}
.hero-desc {
  font-size:12px; color:var(--dim); line-height:2;
  max-width:500px; margin:0 auto 44px;
  animation:fadeUp 0.7s ease 0.9s both;
}
.cta-row {
  display:flex; gap:12px; justify-content:center; flex-wrap:wrap;
  animation:fadeUp 0.7s ease 1.1s both;
}

/* ── REPORT BANNER ── */
.report-banner {
  position:relative; z-index:1;
  margin:0; padding:22px 48px;
  background:var(--bg2);
  border-top:1px solid rgba(255,170,0,0.2);
  border-bottom:1px solid rgba(255,170,0,0.2);
  display:flex; align-items:center; justify-content:space-between; gap:24px;
  animation:fadeUp 0.5s ease 1.3s both;
  overflow:hidden;
}
.report-banner::before {
  content:'';
  position:absolute; inset:0;
  background: linear-gradient(90deg,
    rgba(255,170,0,0.03) 0%,
    rgba(255,170,0,0.06) 50%,
    rgba(255,170,0,0.03) 100%);
  background-size:300% 100%;
  animation:border-run 4s linear infinite;
}
.report-banner-left { display:flex; align-items:center; gap:16px; position:relative; z-index:1; }
.report-icon { font-size:28px; }
.report-text h4 {
  font-family:'Orbitron',monospace; font-size:13px; font-weight:700;
  color:var(--amber); letter-spacing:2px; margin-bottom:4px;
  text-shadow:0 0 10px rgba(255,170,0,0.4);
}
.report-text p { font-size:10px; color:var(--dim); letter-spacing:1px; }
.report-banner-right { display:flex; gap:10px; position:relative; z-index:1; flex-shrink:0; }
.report-btn {
  display:inline-flex; align-items:center; gap:8px;
  padding:11px 22px; border-radius:3px;
  font-family:'Share Tech Mono',monospace; font-size:11px; letter-spacing:2px;
  text-decoration:none; cursor:pointer; border:none; transition:all 0.2s;
}
.report-btn-primary {
  background:transparent; border:1px solid rgba(255,170,0,0.5); color:var(--amber);
  text-shadow:0 0 8px rgba(255,170,0,0.5);
  box-shadow:0 0 12px rgba(255,170,0,0.15);
}
.report-btn-primary:hover {
  background:rgba(255,170,0,0.1);
  box-shadow:0 0 24px rgba(255,170,0,0.4);
  transform:translateY(-2px);
}
.report-btn-ghost {
  background:transparent; border:1px solid var(--border2); color:var(--dim);
}
.report-btn-ghost:hover {
  border-color:rgba(255,170,0,0.4); color:var(--amber);
}

.stats-row {
  position:relative; z-index:1;
  display:flex; justify-content:center;
  border-top:1px solid var(--border); border-bottom:1px solid var(--border);
  background:var(--bg2);
}
.stat { flex:1; max-width:200px; padding:36px 20px; text-align:center; border-right:1px solid var(--border); }
.stat:last-child { border-right:none; }
.stat-n {
  font-family:'Orbitron',monospace; font-size:42px; font-weight:900;
  color:var(--g); text-shadow:0 0 20px rgba(0,255,65,0.5);
  line-height:1; margin-bottom:8px;
}
.stat-l { font-size:9px; color:var(--g3); letter-spacing:3px; text-transform:uppercase; }

.features { position:relative; z-index:1; max-width:1100px; margin:0 auto; padding:80px 40px; }
.feat-head { font-size:9px; color:var(--g3); letter-spacing:4px; text-transform:uppercase; margin-bottom:40px; text-align:center; }
.feat-grid {
  display:grid; grid-template-columns:repeat(3,1fr);
  gap:1px; background:var(--border); border:1px solid var(--border); border-radius:4px; overflow:hidden;
}
.feat-card { background:var(--panel); padding:32px; transition:background 0.2s; }
.feat-card:hover { background:var(--bg3); }
.feat-icon { font-size:24px; margin-bottom:16px; }
.feat-name { font-family:'Orbitron',monospace; font-size:12px; font-weight:700; color:var(--g); margin-bottom:10px; letter-spacing:2px; }
.feat-desc { font-size:11px; color:var(--dim); line-height:1.8; }
.feat-tag { display:inline-block; margin-top:14px; font-size:8px; letter-spacing:2px; padding:3px 10px; border:1px solid var(--border2); color:var(--g3); border-radius:2px; }

.arch { position:relative; z-index:1; text-align:center; padding:60px 40px; border-top:1px solid var(--border); border-bottom:1px solid var(--border); background:var(--bg2); }
.arch-flow { display:inline-flex; align-items:center; gap:10px; padding:16px 28px; border:1px solid var(--border); border-radius:4px; background:var(--bg3); }
.arch-node { padding:10px 18px; border-radius:2px; font-size:11px; letter-spacing:2px; border:1px solid; }
.arch-node.c { border-color:var(--border2); color:var(--dim); }
.arch-node.w { border-color:var(--g2); color:var(--g); text-shadow:0 0 10px rgba(0,255,65,0.5); box-shadow:0 0 16px rgba(0,255,65,0.15); }
.arch-arr { color:var(--g3); font-size:18px; }

footer { position:relative; z-index:1; text-align:center; padding:28px; border-top:1px solid var(--border); font-size:10px; color:var(--g3); letter-spacing:3px; background:var(--bg2); }
</style>
</head>
<body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>

<nav>
  <div class="logo">W-IPS</div>
  <div class="nav-status"><div class="status-dot"></div> SYSTEM ONLINE</div>
  <div class="nav-links">
    <a href="http://localhost:8080/login">DEMO</a>
    <a href="http://localhost:5002">DASHBOARD</a>
    <a href="http://localhost:5003" class="nav-report-btn">&#9889; REPORT</a>
  </div>
</nav>

<section class="hero">
  <div class="terminal-box">
    <div class="term-bar">
      <div class="term-dot" style="background:#ff5f57"></div>
      <div class="term-dot" style="background:#febc2e"></div>
      <div class="term-dot" style="background:#28c840"></div>
      <div class="term-title">root@waf-system:~</div>
    </div>
    <div class="term-body">
      <div class="term-line"><span class="term-prompt">root@waf:~$</span><span style="color:var(--g)"> ./ips --init</span></div>
      <div class="term-out"><span class="term-ok">[OK]</span> Loading rule engine...</div>
      <div class="term-out"><span class="term-ok">[OK]</span> SQL injection patterns: 11</div>
      <div class="term-out"><span class="term-ok">[OK]</span> XSS patterns: 10</div>
      <div class="term-out"><span class="term-ok">[OK]</span> Rate limiter: active</div>
      <div class="term-out"><span class="term-ok">[OK]</span> IP blocklist: loaded</div>
      <div class="term-out"><span class="term-ok">[OK]</span> Proxy listening on :8080</div>
      <div class="term-out"><span class="term-warn">[NEW]</span> Report server: :5003</div>
      <div class="term-line" style="margin-top:4px;">
        <span class="term-prompt">root@waf:~$</span><span class="term-cursor"></span>
      </div>
    </div>
  </div>

  <div class="hero-title">INTRUSION</div>
  <div class="hero-sub">Prevention System</div>
  <p class="hero-desc">Python-based WAF. Intercepts, analyzes, and neutralizes<br>malicious HTTP traffic before it reaches your backend.</p>
  <div class="cta-row">
    <a href="http://localhost:8080/login" class="btn btn-primary">[ LAUNCH DEMO ]</a>
    <a href="http://localhost:5002" class="btn btn-ghost">[ DASHBOARD ]</a>
    <a href="http://localhost:5003" class="btn btn-amber">[ REPORT ]</a>
  </div>
</section>

<!-- ── REPORT BANNER ── -->
<div class="report-banner">
  <div class="report-banner-left">
    <div class="report-icon">&#9889;</div>
    <div class="report-text">
      <h4>LIVE ATTACK REPORT</h4>
      <p>Real-time analysis &middot; Attack breakdown &middot; IP statistics &middot; PDF export</p>
    </div>
  </div>
  <div class="report-banner-right">
    <a href="http://localhost:5003" class="report-btn report-btn-primary">[ VIEW FULL REPORT ]</a>
    <a href="http://localhost:5003/download/pdf" class="report-btn report-btn-ghost">[ DOWNLOAD PDF ]</a>
  </div>
</div>

<div class="stats-row">
  <div class="stat"><div class="stat-n">6+</div><div class="stat-l">Attack Types</div></div>
  <div class="stat"><div class="stat-n">3</div><div class="stat-l">Strike Rule</div></div>
  <div class="stat"><div class="stat-n">8080</div><div class="stat-l">WAF Port</div></div>
  <div class="stat"><div class="stat-n">100%</div><div class="stat-l">Block Rate</div></div>
</div>

<section class="features">
  <div class="feat-head">::: THREAT COVERAGE :::</div>
  <div class="feat-grid">
    <div class="feat-card"><div class="feat-icon">&#128137;</div><div class="feat-name">SQL INJECTION</div><div class="feat-desc">OR 1=1 &middot; UNION SELECT &middot; DROP TABLE &middot; SLEEP() &middot; INSERT INTO</div><span class="feat-tag">NEUTRALIZED</span></div>
    <div class="feat-card"><div class="feat-icon">&#128221;</div><div class="feat-name">XSS ATTACK</div><div class="feat-desc">&lt;script&gt; &middot; javascript: &middot; onerror= &middot; eval() &middot; document.cookie</div><span class="feat-tag">NEUTRALIZED</span></div>
    <div class="feat-card"><div class="feat-icon">&#128187;</div><div class="feat-name">CMD INJECTION</div><div class="feat-desc">; ls &middot; | whoami &middot; &amp;&amp; dir &middot; backtick exec &middot; $() subshell</div><span class="feat-tag">NEUTRALIZED</span></div>
    <div class="feat-card"><div class="feat-icon">&#128194;</div><div class="feat-name">PATH TRAVERSAL</div><div class="feat-desc">../../etc/passwd &middot; %2e%2e%2f &middot; windows/system32</div><span class="feat-tag">NEUTRALIZED</span></div>
    <div class="feat-card"><div class="feat-icon">&#128678;</div><div class="feat-name">RATE LIMIT / DoS</div><div class="feat-desc">Excessive request throttling per IP. Blocks denial-of-service floods.</div><span class="feat-tag">THROTTLED</span></div>
    <div class="feat-card"><div class="feat-icon">&#128683;</div><div class="feat-name">IP BLACKLIST</div><div class="feat-desc">Permanent ban after 3 strikes. Persists to disk. Survives restarts.</div><span class="feat-tag">PERMANENT BAN</span></div>
  </div>
</section>

<div class="arch">
  <div class="feat-head" style="margin-bottom:28px;">::: TRAFFIC FLOW :::</div>
  <div class="arch-flow">
    <div class="arch-node c">CLIENT</div><div class="arch-arr">&#x2501;&#x2501;&#x25B6;</div>
    <div class="arch-node w">WAF :8080</div><div class="arch-arr">&#x2501;&#x2501;&#x25B6;</div>
    <div class="arch-node c">BACKEND :5001</div>
  </div>
  <div style="margin-top:16px;font-size:10px;color:var(--g3);letter-spacing:2px;">MALICIOUS REQUESTS TERMINATED AT THE PROXY LAYER</div>
</div>

<footer>WEB APPLICATION IPS &nbsp;&middot;&nbsp; SEM 4 MINI PROJECT &nbsp;&middot;&nbsp; MIT LICENSE</footer>
</body>
</html>""")

LOGIN_PAGE = ("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Attack Console</title>
""" + SHARED_CSS + MATRIX_JS + """
<style>
body { display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; padding:100px 20px 40px; }
.wrapper {
  position:relative; z-index:1;
  display:flex; gap:56px; align-items:flex-start;
  max-width:940px; width:100%;
  opacity:0; animation:fadeUp 0.6s ease 0.1s forwards;
}
.left { flex:1; padding-top:8px; }
.back { font-size:10px; color:var(--g3); text-decoration:none; letter-spacing:2px; display:inline-flex; align-items:center; gap:6px; margin-bottom:40px; transition:color 0.2s; }
.back:hover { color:var(--g); }
.left h2 { font-family:'Orbitron',monospace; font-size:28px; font-weight:900; line-height:1.1; margin-bottom:12px; text-shadow:0 0 20px rgba(0,255,65,0.4); }
.left p { font-size:11px; color:var(--dim); line-height:2; margin-bottom:28px; }
.cs-title { font-size:8px; color:var(--g3); letter-spacing:4px; text-transform:uppercase; margin-bottom:12px; }
.attacks { display:flex; flex-direction:column; gap:8px; }
.atk {
  display:flex; align-items:center; gap:14px; padding:12px 16px;
  background:var(--panel); border:1px solid var(--border); border-radius:3px;
  cursor:pointer; transition:all 0.2s; position:relative; overflow:hidden;
}
.atk::before { content:''; position:absolute; left:0; top:0; bottom:0; width:2px; background:var(--g); opacity:0; transition:opacity 0.2s; }
.atk:hover { border-color:var(--border2); background:var(--bg3); }
.atk:hover::before { opacity:1; }
.atk-icon { font-size:16px; flex-shrink:0; }
.atk-name { font-size:11px; color:var(--g); margin-bottom:2px; letter-spacing:1px; }
.atk-payload { font-size:9px; color:var(--muted); }
.atk-hint { font-size:8px; color:var(--g3); border:1px solid var(--border); padding:2px 8px; letter-spacing:1px; white-space:nowrap; transition:all 0.2s; }
.atk:hover .atk-hint { border-color:var(--border2); color:var(--g); }
.card {
  width:370px; flex-shrink:0;
  background:var(--panel); border:1px solid var(--border); border-radius:4px;
  padding:40px 36px; position:relative; overflow:hidden;
}
.card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--g),transparent); }
.card-tag { font-size:8px; color:var(--g3); letter-spacing:4px; text-transform:uppercase; margin-bottom:10px; }
.card h3 { font-family:'Orbitron',monospace; font-size:18px; font-weight:900; margin-bottom:4px; text-shadow:0 0 16px rgba(0,255,65,0.3); }
.card-sub { font-size:10px; color:var(--g3); letter-spacing:1px; margin-bottom:32px; }
.btn-login {
  width:100%; padding:14px; background:transparent;
  border:1px solid var(--g); border-radius:3px;
  font-family:'Share Tech Mono',monospace; font-size:13px; letter-spacing:3px;
  color:var(--g); cursor:pointer;
  text-shadow:0 0 8px var(--g);
  box-shadow:0 0 12px rgba(0,255,65,0.2),inset 0 0 12px rgba(0,255,65,0.05);
  transition:all 0.2s;
}
.btn-login:hover { background:rgba(0,255,65,0.08); box-shadow:0 0 24px rgba(0,255,65,0.5),inset 0 0 20px rgba(0,255,65,0.1); }
.divider { display:flex; align-items:center; gap:10px; margin:20px 0; font-size:9px; color:var(--g3); letter-spacing:2px; }
.divider::before,.divider::after { content:''; flex:1; height:1px; background:var(--border); }
.btn-normal { width:100%; padding:12px; background:transparent; border:1px solid var(--border); border-radius:3px; font-family:'Share Tech Mono',monospace; font-size:11px; letter-spacing:2px; color:var(--dim); cursor:pointer; transition:all 0.2s; }
.btn-normal:hover { border-color:var(--border2); color:var(--g); }
.result-box { margin-top:18px; padding:14px 16px; border-radius:3px; font-size:11px; line-height:1.8; animation:fadeUp 0.3s ease; }
.res-ok { background:rgba(0,255,65,0.05); border:1px solid rgba(0,255,65,0.2); color:var(--g); }
.res-err { background:rgba(255,0,64,0.05); border:1px solid rgba(255,0,64,0.2); color:var(--red); }
.warn { margin-top:18px; padding:10px 14px; border-radius:3px; background:rgba(255,170,0,0.04); border:1px solid rgba(255,170,0,0.15); font-size:9px; color:rgba(255,170,0,0.6); line-height:1.8; letter-spacing:0.5px; }
</style>
</head>
<body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<nav>
  <div class="logo">W-IPS</div>
  <div class="nav-status"><div class="status-dot"></div> WAF ACTIVE</div>
  <div class="nav-links">
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:5002">DASHBOARD</a>
    <a href="http://localhost:5003" class="nav-report-btn">&#9889; REPORT</a>
  </div>
</nav>
<div class="wrapper">
  <div class="left">
    <a href="http://localhost:5001" class="back">&#9664; BACK TO HOME</a>
    <h2>ATTACK<br>CONSOLE</h2>
    <p>Click a payload to auto-fill. Submit via WAF<br>on :8080 to test intrusion detection.</p>
    <div class="cs-title">::: PAYLOAD LIBRARY :::</div>
    <div class="attacks">
      <div class="atk" onclick="fill('1 OR 1=1')"><div class="atk-icon">&#128137;</div><div style="flex:1"><div class="atk-name">SQL INJECTION</div><div class="atk-payload">1 OR 1=1</div></div><div class="atk-hint">INJECT</div></div>
      <div class="atk" onclick="fill('<script>alert(1)<\/script>')"><div class="atk-icon">&#128221;</div><div style="flex:1"><div class="atk-name">XSS ATTACK</div><div class="atk-payload">&lt;script&gt;alert(1)&lt;/script&gt;</div></div><div class="atk-hint">INJECT</div></div>
      <div class="atk" onclick="fill('; ls')"><div class="atk-icon">&#128187;</div><div style="flex:1"><div class="atk-name">CMD INJECTION</div><div class="atk-payload">; ls</div></div><div class="atk-hint">INJECT</div></div>
      <div class="atk" onclick="fill('../../etc/passwd')"><div class="atk-icon">&#128194;</div><div style="flex:1"><div class="atk-name">PATH TRAVERSAL</div><div class="atk-payload">../../etc/passwd</div></div><div class="atk-hint">INJECT</div></div>
      <div class="atk" onclick="fill('1 UNION SELECT username,password FROM users--')"><div class="atk-icon">&#128450;&#65039;</div><div style="flex:1"><div class="atk-name">UNION SELECT</div><div class="atk-payload">1 UNION SELECT username,password FROM users--</div></div><div class="atk-hint">INJECT</div></div>
      <div class="atk" onclick="fill('1; DROP TABLE users--')"><div class="atk-icon">&#128163;</div><div style="flex:1"><div class="atk-name">DROP TABLE</div><div class="atk-payload">1; DROP TABLE users--</div></div><div class="atk-hint">INJECT</div></div>
    </div>
  </div>
  <div class="card">
    <div class="card-tag">::: DEMO LOGIN PORTAL :::</div>
    <h3>SYSTEM<br>ACCESS</h3>
    <div class="card-sub">REQUESTS ROUTED THROUGH WAF :8080</div>
    <form method="GET" action="http://localhost:8080/login">
      <label>USERNAME / PAYLOAD</label>
      <input type="text" name="user" id="uname" placeholder="admin" required style="margin-bottom:16px;">
      <label>PASSWORD</label>
      <input type="password" name="pass" placeholder="&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;" style="margin-bottom:20px;">
      <button type="submit" class="btn-login">[ AUTHENTICATE ]</button>
    </form>
    {% if result %}
    <div class="result-box {{ 'res-ok' if result_type == 'success' else 'res-err' }}">{{ result }}</div>
    {% endif %}
    <div class="divider">OR</div>
    <button class="btn-normal" onclick="document.getElementById('uname').value='1';document.querySelector('form').submit();">[ NORMAL LOGIN — USER ID 1 ]</button>
    <div class="warn">&#9888; INTENTIONALLY VULNERABLE DEMO — FOR IPS TESTING ONLY</div>
  </div>
</div>
<script>function fill(v){document.getElementById('uname').value=v;document.getElementById('uname').focus();}</script>
</body>
</html>""")


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)

@app.route("/login")
def login():
    user = request.args.get("user")
    if not user:
        return render_template_string(LOGIN_PAGE, result=None)
    query = f"SELECT * FROM users WHERE id = {user}"
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    try:
        result = cursor.execute(query).fetchall()
        if result:
            return render_template_string(LOGIN_PAGE,
                result=f"[ACCESS GRANTED] User: {result[0][1]}", result_type="success")
        else:
            return render_template_string(LOGIN_PAGE,
                result="[ACCESS DENIED] No user found", result_type="error")
    except Exception as e:
        return render_template_string(LOGIN_PAGE,
            result=f"[DB ERROR] {str(e)}", result_type="error")

if __name__ == "__main__":
    app.run(port=5001)
