"""
admin.py — IPS Admin Panel (Port 5004)
Routes:
  /          → login page
  /dashboard → admin dashboard (protected)
  /unblock   → unblock an IP
  /clear     → clear attack logs
  /logout    → logout
"""
from flask import Flask, request, render_template_string, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ips-admin-secret-2024'

ADMIN_PASSWORD = 'admin123'
BLOCK_FILE     = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blocked_ips.json')
LOG_FILE       = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attacks.log')

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
  --red:#ff0040;--amber:#ffaa00;--cyan:#00ffff;--text:#c8ffc8;}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Share Tech Mono',monospace;background:var(--bg);color:var(--g);min-height:100vh;cursor:crosshair;overflow-x:hidden;}
#matrix{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:0.12;}
body::after{content:'';position:fixed;inset:0;z-index:999;pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);}
body::before{content:'';position:fixed;inset:0;z-index:998;pointer-events:none;
  background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.6) 100%);}
@keyframes glitch{0%,100%{text-shadow:none;transform:none;}20%{text-shadow:-2px 0 var(--red),2px 0 var(--cyan);transform:translate(-1px,0);}40%{text-shadow:2px 0 var(--red),-2px 0 var(--cyan);transform:translate(1px,0);}60%{text-shadow:none;transform:none;}80%{text-shadow:-1px 0 var(--cyan);transform:translate(1px,0);}}
@keyframes flicker{0%,100%{opacity:1}41%{opacity:1}42%{opacity:0.6}43%{opacity:1}75%{opacity:1}76%{opacity:0.7}77%{opacity:1}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}
@keyframes scanH{0%{top:-4px}100%{top:100%}}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.scan-line{position:fixed;left:0;right:0;height:2px;z-index:997;pointer-events:none;
  background:linear-gradient(90deg,transparent,rgba(0,255,65,0.35),transparent);animation:scanH 8s linear infinite;}
nav{position:sticky;top:0;z-index:200;display:flex;justify-content:space-between;align-items:center;
  padding:14px 48px;background:rgba(5,10,5,0.93);backdrop-filter:blur(14px);
  border-bottom:1px solid var(--border);animation:flicker 10s infinite;}
.logo{font-family:'Orbitron',monospace;font-size:14px;font-weight:900;color:var(--red);letter-spacing:4px;
  text-shadow:0 0 20px var(--red),0 0 40px rgba(255,0,64,0.3);animation:glitch 7s infinite;}
.nav-links{display:flex;gap:24px;align-items:center;}
.nav-links a{font-size:10px;color:var(--dim);text-decoration:none;letter-spacing:2px;transition:color 0.2s;}
.nav-links a:hover{color:var(--g);}
.nav-badge{font-size:9px;color:var(--amber);border:1px solid rgba(255,170,0,0.4);padding:4px 12px;border-radius:2px;letter-spacing:2px;}
main{position:relative;z-index:1;max-width:1300px;margin:0 auto;padding:44px 48px;}
.page-head{margin-bottom:32px;opacity:0;animation:fadeUp 0.5s ease 0.1s forwards;}
.page-head h1{font-family:'Orbitron',monospace;font-size:28px;font-weight:900;letter-spacing:2px;
  text-shadow:0 0 24px rgba(255,0,64,0.4);margin-bottom:6px;color:var(--red);}
.page-head p{font-size:11px;color:var(--dim);letter-spacing:1px;}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:24px 28px;margin-bottom:20px;
  position:relative;overflow:hidden;opacity:0;animation:fadeUp 0.4s ease forwards;}
.panel::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--g),transparent);opacity:0.4;}
.panel-title{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--g);
  letter-spacing:3px;margin-bottom:18px;}
.stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;
  opacity:0;animation:fadeUp 0.4s ease 0.15s forwards;}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:4px;padding:20px;
  text-align:center;position:relative;overflow:hidden;}
.stat::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;}
.s-r::before{background:linear-gradient(90deg,var(--red),transparent);}
.s-a::before{background:linear-gradient(90deg,var(--amber),transparent);}
.s-g::before{background:linear-gradient(90deg,var(--g),transparent);}
.s-c::before{background:linear-gradient(90deg,var(--cyan),transparent);}
.stat-n{font-family:'Orbitron',monospace;font-size:36px;font-weight:900;line-height:1;margin-bottom:6px;}
.s-r .stat-n{color:var(--red);text-shadow:0 0 14px rgba(255,0,64,0.5);}
.s-a .stat-n{color:var(--amber);text-shadow:0 0 14px rgba(255,170,0,0.5);}
.s-g .stat-n{color:var(--g);text-shadow:0 0 14px rgba(0,255,65,0.5);}
.s-c .stat-n{color:var(--cyan);text-shadow:0 0 14px rgba(0,255,255,0.5);}
.stat-l{font-size:8px;color:var(--g3);letter-spacing:2px;text-transform:uppercase;}
table{width:100%;border-collapse:collapse;}
thead th{padding:10px 16px;text-align:left;font-size:8px;color:var(--g3);letter-spacing:3px;
  text-transform:uppercase;border-bottom:1px solid var(--border);background:var(--bg3);}
tbody tr{border-bottom:1px solid rgba(0,255,65,0.05);transition:background 0.15s;}
tbody tr:hover{background:rgba(0,255,65,0.03);}
td{padding:11px 16px;font-size:11px;color:var(--text);}
.td-mono{font-size:9px;color:var(--dim);}
.td-ip{font-size:11px;color:var(--red);}
.btn{display:inline-flex;align-items:center;gap:6px;padding:7px 16px;border-radius:3px;
  font-family:'Share Tech Mono',monospace;font-size:10px;letter-spacing:1px;
  cursor:pointer;border:none;text-decoration:none;transition:all 0.2s;}
.btn-danger{background:transparent;border:1px solid rgba(255,0,64,0.5);color:var(--red);}
.btn-danger:hover{background:rgba(255,0,64,0.08);box-shadow:0 0 14px rgba(255,0,64,0.3);}
.btn-success{background:transparent;border:1px solid rgba(0,255,65,0.5);color:var(--g);}
.btn-success:hover{background:rgba(0,255,65,0.08);box-shadow:0 0 14px rgba(0,255,65,0.3);}
.btn-amber{background:transparent;border:1px solid rgba(255,170,0,0.5);color:var(--amber);}
.btn-amber:hover{background:rgba(255,170,0,0.08);box-shadow:0 0 14px rgba(255,170,0,0.3);}
.alert{padding:12px 18px;border-radius:3px;font-size:11px;margin-bottom:20px;letter-spacing:1px;}
.alert-success{background:rgba(0,255,65,0.06);border:1px solid rgba(0,255,65,0.2);color:var(--g);}
.alert-danger{background:rgba(255,0,64,0.06);border:1px solid rgba(255,0,64,0.2);color:var(--red);}
input[type=text],input[type=password]{width:100%;padding:11px 14px;background:var(--bg3);
  border:1px solid var(--border);border-radius:3px;color:var(--g);
  font-family:'Share Tech Mono',monospace;font-size:13px;outline:none;
  transition:border-color 0.2s;caret-color:var(--g);margin-bottom:14px;}
input:focus{border-color:var(--g2);box-shadow:0 0 14px rgba(0,255,65,0.2);}
input::placeholder{color:var(--muted,rgba(0,255,65,0.3));}
label{display:block;font-size:9px;color:var(--g3);letter-spacing:3px;text-transform:uppercase;margin-bottom:7px;}
</style>
"""

LOGIN_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Admin Login</title>""" + BASE_STYLE + MATRIX_JS + """
<style>
body{display:flex;align-items:center;justify-content:center;min-height:100vh;}
.login-card{position:relative;z-index:1;background:var(--panel);border:1px solid rgba(255,0,64,0.3);
  border-radius:4px;padding:44px 40px;width:360px;}
.login-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--red),transparent);}
.login-title{font-family:'Orbitron',monospace;font-size:18px;font-weight:900;color:var(--red);
  letter-spacing:3px;text-shadow:0 0 16px rgba(255,0,64,0.4);margin-bottom:4px;}
.login-sub{font-size:9px;color:var(--g3);letter-spacing:2px;margin-bottom:32px;}
.btn-login{width:100%;padding:13px;background:transparent;border:1px solid var(--red);border-radius:3px;
  font-family:'Share Tech Mono',monospace;font-size:12px;letter-spacing:3px;color:var(--red);
  cursor:pointer;text-shadow:0 0 8px rgba(255,0,64,0.5);
  box-shadow:0 0 12px rgba(255,0,64,0.15);transition:all 0.2s;}
.btn-login:hover{background:rgba(255,0,64,0.08);box-shadow:0 0 24px rgba(255,0,64,0.4);}
.err{margin-bottom:16px;padding:10px 14px;background:rgba(255,0,64,0.06);
  border:1px solid rgba(255,0,64,0.2);border-radius:3px;font-size:10px;color:var(--red);letter-spacing:1px;}
</style></head><body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<div class="login-card">
  <div class="login-title">ADMIN ACCESS</div>
  <div class="login-sub">IPS CONTROL PANEL — AUTHORIZED ONLY</div>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <label>Admin Password</label>
    <input type="password" name="password" placeholder="&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;" required>
    <button type="submit" class="btn-login">[ ACCESS CONTROL PANEL ]</button>
  </form>
</div>
</body></html>"""

ADMIN_PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>[IPS] :: Admin Panel</title>""" + BASE_STYLE + MATRIX_JS + """
</head><body>
<canvas id="matrix"></canvas>
<div class="scan-line"></div>
<nav>
  <div class="logo">ADMIN PANEL</div>
  <div class="nav-links">
    <span class="nav-badge">&#128274; AUTHORIZED</span>
    <a href="http://localhost:5001">HOME</a>
    <a href="http://localhost:5002">DASHBOARD</a>
    <a href="/logout">LOGOUT</a>
  </div>
</nav>
<main>
  <div class="page-head">
    <h1>CONTROL CENTER</h1>
    <p>MANAGE BLOCKED IPS, LOGS AND SYSTEM SETTINGS</p>
  </div>

  {% if msg %}<div class="alert alert-{{ msg_type }}">{{ msg }}</div>{% endif %}

  <!-- Stats -->
  <div class="stat-row">
    <div class="stat s-r"><div class="stat-n">{{ total_attacks }}</div><div class="stat-l">Total Attacks</div></div>
    <div class="stat s-a"><div class="stat-n">{{ blocked_count }}</div><div class="stat-l">Blocked IPs</div></div>
    <div class="stat s-g"><div class="stat-n">{{ log_size }}</div><div class="stat-l">Log Entries</div></div>
    <div class="stat s-c"><div class="stat-n">{{ uptime }}</div><div class="stat-l">Server Status</div></div>
  </div>

  <!-- Blocked IPs management -->
  <div class="panel" style="animation-delay:0.2s;">
    <div class="panel-title">&#128683; BLOCKED IP MANAGEMENT</div>
    {% if blocked_ips %}
    <table>
      <thead><tr><th>IP ADDRESS</th><th>ATTACK COUNT</th><th>ACTION</th></tr></thead>
      <tbody>
        {% for ip in blocked_ips %}
        <tr>
          <td class="td-ip">{{ ip }}</td>
          <td class="td-mono">{{ attack_count.get(ip, '?') }} attacks</td>
          <td>
            <form method="POST" action="/unblock" style="display:inline;">
              <input type="hidden" name="ip" value="{{ ip }}">
              <button type="submit" class="btn btn-success">[ UNBLOCK ]</button>
            </form>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div style="color:var(--dim);font-size:11px;padding:20px 0;">No IPs currently blocked.</div>
    {% endif %}
  </div>

  <!-- Manual IP block -->
  <div class="panel" style="animation-delay:0.3s;">
    <div class="panel-title">&#128274; MANUALLY BLOCK AN IP</div>
    <form method="POST" action="/block" style="display:flex;gap:12px;align-items:flex-end;">
      <div style="flex:1;">
        <label>IP Address to Block</label>
        <input type="text" name="ip" placeholder="e.g. 192.168.1.100" style="margin-bottom:0;">
      </div>
      <button type="submit" class="btn btn-danger" style="height:42px;margin-bottom:0;">[ BLOCK IP ]</button>
    </form>
  </div>

  <!-- Log management -->
  <div class="panel" style="animation-delay:0.4s;">
    <div class="panel-title">&#128203; LOG MANAGEMENT</div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
      <a href="http://localhost:5003/download/pdf" class="btn btn-amber">[ DOWNLOAD REPORT PDF ]</a>
      <form method="POST" action="/clear-logs" style="display:inline;" onsubmit="return confirm('Clear all attack logs?');">
        <button type="submit" class="btn btn-danger">[ CLEAR ATTACK LOGS ]</button>
      </form>
      <form method="POST" action="/clear-blocked" style="display:inline;" onsubmit="return confirm('Unblock ALL IPs?');">
        <button type="submit" class="btn btn-danger">[ UNBLOCK ALL IPs ]</button>
      </form>
    </div>
  </div>

  <!-- Recent attacks -->
  <div class="panel" style="animation-delay:0.5s;">
    <div class="panel-title">&#9889; RECENT ATTACKS (LAST 10)</div>
    {% if recent_logs %}
    <table>
      <thead><tr><th>#</th><th>TIME</th><th>IP</th><th>TYPE</th><th>SEVERITY</th><th>COUNTRY</th></tr></thead>
      <tbody>
        {% for log in recent_logs %}
        <tr>
          <td class="td-mono">{{ loop.index }}</td>
          <td class="td-mono">{{ log.time }}</td>
          <td class="td-ip">{{ log.ip }}</td>
          <td style="font-size:10px;color:var(--amber);">{{ log.get('attack_type','?') }}</td>
          <td style="font-size:9px;color:var(--red);">{{ log.get('severity','?') }}</td>
          <td class="td-mono">{{ log.get('country','?') }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <div style="color:var(--dim);font-size:11px;padding:20px 0;">No attacks logged yet.</div>
    {% endif %}
  </div>
</main>
</body></html>"""


def load_data():
    blocked_ips, attack_count = set(), {}
    try:
        with open(BLOCK_FILE) as f:
            data = json.load(f)
            blocked_ips  = set(data.get('blocked_ips', []))
            attack_count = data.get('attack_count', {})
    except: pass
    logs = []
    try:
        with open(LOG_FILE) as f:
            for line in f:
                l = line.strip()
                if l:
                    try: logs.append(json.loads(l))
                    except: pass
    except: pass
    return blocked_ips, attack_count, logs


@app.route('/')
def index():
    if not session.get('admin'):
        return redirect('/login')
    return redirect('/dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/dashboard')
        return render_template_string(LOGIN_PAGE, error='[ACCESS DENIED] Invalid password')
    return render_template_string(LOGIN_PAGE, error=None)


@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')
    blocked_ips, attack_count, logs = load_data()
    return render_template_string(ADMIN_PAGE,
        blocked_ips=sorted(blocked_ips),
        attack_count=attack_count,
        total_attacks=len(logs),
        blocked_count=len(blocked_ips),
        log_size=len(logs),
        uptime='ONLINE',
        recent_logs=list(reversed(logs))[:10],
        msg=request.args.get('msg'),
        msg_type=request.args.get('t', 'success'),
    )


@app.route('/unblock', methods=['POST'])
def unblock():
    if not session.get('admin'): return redirect('/login')
    ip = request.form.get('ip', '').strip()
    try:
        with open(BLOCK_FILE) as f: data = json.load(f)
        data['blocked_ips'] = [x for x in data.get('blocked_ips', []) if x != ip]
        data['attack_count'].pop(ip, None)
        with open(BLOCK_FILE, 'w') as f: json.dump(data, f)
        return redirect(f'/dashboard?msg=[OK] {ip} has been unblocked&t=success')
    except:
        return redirect('/dashboard?msg=[ERR] Could not unblock IP&t=danger')


@app.route('/block', methods=['POST'])
def block_ip():
    if not session.get('admin'): return redirect('/login')
    ip = request.form.get('ip', '').strip()
    if not ip: return redirect('/dashboard?msg=[ERR] No IP provided&t=danger')
    try:
        data = {'blocked_ips': [], 'attack_count': {}}
        if os.path.exists(BLOCK_FILE):
            with open(BLOCK_FILE) as f: data = json.load(f)
        if ip not in data['blocked_ips']:
            data['blocked_ips'].append(ip)
        data['attack_count'][ip] = data['attack_count'].get(ip, 0) + 99
        with open(BLOCK_FILE, 'w') as f: json.dump(data, f)
        return redirect(f'/dashboard?msg=[OK] {ip} has been blocked&t=success')
    except:
        return redirect('/dashboard?msg=[ERR] Could not block IP&t=danger')


@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    if not session.get('admin'): return redirect('/login')
    try:
        open(LOG_FILE, 'w').close()
        return redirect('/dashboard?msg=[OK] Attack logs cleared&t=success')
    except:
        return redirect('/dashboard?msg=[ERR] Could not clear logs&t=danger')


@app.route('/clear-blocked', methods=['POST'])
def clear_blocked():
    if not session.get('admin'): return redirect('/login')
    try:
        with open(BLOCK_FILE, 'w') as f:
            json.dump({'blocked_ips': [], 'attack_count': {}}, f)
        return redirect('/dashboard?msg=[OK] All IPs unblocked&t=success')
    except:
        return redirect('/dashboard?msg=[ERR] Could not clear blocked IPs&t=danger')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    print()
    print('  +======================================+')
    print('  |  IPS Admin Panel    --  Port 5004   |')
    print('  |  http://localhost:5004               |')
    print('  |  Password: admin123                  |')
    print('  +======================================+')
    print()
    app.run(port=5004, debug=False)
