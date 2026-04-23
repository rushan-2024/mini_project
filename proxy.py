from flask import Flask, request, Response
import requests
import json
import os
from rules_engine import detect_attack, is_honeypot
from logger import log_attack
from rate_limiter import check_rate, check_brute_force

TARGET     = 'http://localhost:5001'
BLOCK_FILE = 'blocked_ips.json'

app = Flask(__name__)

def load_blocked():
    """Always reads from disk — so admin unblock takes effect immediately."""
    if os.path.exists(BLOCK_FILE):
        try:
            with open(BLOCK_FILE) as f:
                content = f.read().strip()
                if not content:
                    return set(), {}
                data = json.loads(content)
                return set(data.get('blocked_ips', [])), data.get('attack_count', {})
        except:
            pass
    return set(), {}

def save_blocked(blocked_ips, attack_count):
    with open(BLOCK_FILE, 'w') as f:
        json.dump({'blocked_ips': list(blocked_ips), 'attack_count': attack_count}, f)

def blocked_page(ip, attack_type, severity='HIGH'):
    sev_color = {'CRITICAL':'#ff0040','HIGH':'#ffaa00','MEDIUM':'#00ffff','LOW':'#00ff41'}.get(severity,'#ff0040')
    return f"""<!DOCTYPE html><html><head><title>Blocked</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Share Tech Mono',monospace;background:#050a05;display:flex;justify-content:center;align-items:center;height:100vh;cursor:crosshair;}}
body::after{{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);z-index:99;}}
.card{{background:#0c160c;border:1px solid {sev_color};border-radius:4px;padding:50px 60px;text-align:center;max-width:520px;position:relative;box-shadow:0 0 40px {sev_color}33;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,{sev_color},transparent);}}
.icon{{font-size:56px;margin-bottom:20px;}}
h1{{font-family:'Orbitron',monospace;font-size:22px;color:{sev_color};text-shadow:0 0 20px {sev_color}88;margin-bottom:14px;letter-spacing:3px;}}
.sev{{display:inline-block;padding:4px 16px;border:1px solid {sev_color};color:{sev_color};font-size:10px;letter-spacing:3px;margin-bottom:16px;}}
p{{color:rgba(0,255,65,0.4);font-size:12px;line-height:1.8;margin-bottom:8px;}}
.ip{{color:{sev_color};font-size:14px;margin:10px 0;}}
.atk{{color:rgba(200,255,200,0.6);font-size:11px;}}
.footer{{margin-top:24px;font-size:9px;color:rgba(0,255,65,0.2);letter-spacing:2px;}}
</style></head><body>
<div class="card">
  <div class="icon">&#128737;&#65039;</div>
  <div class="sev">{severity}</div>
  <h1>ACCESS BLOCKED</h1>
  <p>Your request was identified as a potential attack<br>and has been intercepted by the WAF.</p>
  <div class="ip">{ip}</div>
  <div class="atk">THREAT: {attack_type}</div>
  <div class="footer">WEB APPLICATION INTRUSION PREVENTION SYSTEM</div>
</div></body></html>""", 403

def ip_blocked_page(ip):
    return f"""<!DOCTYPE html><html><head><title>IP Blocked</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Share Tech Mono',monospace;background:#050a05;display:flex;justify-content:center;align-items:center;height:100vh;cursor:crosshair;}}
body::after{{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);z-index:99;}}
.card{{background:#0c160c;border:2px solid #ff0040;border-radius:4px;padding:50px 60px;text-align:center;max-width:520px;box-shadow:0 0 60px #ff004444;position:relative;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#ff0040,transparent);}}
.icon{{font-size:56px;margin-bottom:20px;}}
h1{{font-family:'Orbitron',monospace;font-size:20px;color:#ff0040;text-shadow:0 0 20px #ff004088;margin-bottom:14px;letter-spacing:3px;}}
p{{color:rgba(0,255,65,0.4);font-size:12px;line-height:1.8;margin-bottom:8px;}}
.ip{{color:#ff0040;font-size:18px;font-weight:bold;margin:12px 0;text-shadow:0 0 10px #ff004066;}}
.footer{{margin-top:24px;font-size:9px;color:rgba(0,255,65,0.2);letter-spacing:2px;}}
</style></head><body>
<div class="card">
  <div class="icon">&#128683;</div>
  <h1>IP PERMANENTLY BLOCKED</h1>
  <p>Your IP has been permanently banned due to<br>repeated malicious attack attempts.</p>
  <div class="ip">{ip}</div>
  <div class="footer">WEB APPLICATION INTRUSION PREVENTION SYSTEM</div>
</div></body></html>""", 403

def honeypot_page(ip, path, honeypot_type):
    type_config = {
        'Web Login Honeypot':        ('&#127856;','#ffaa00','ADMIN TRAP ACTIVATED','You accessed a fake admin login page.'),
        'Hidden URL Honeypot':       ('&#128373;','#00ffff','HIDDEN URL TRAP','This URL is a hidden decoy.'),
        'SSH Honeypot':              ('&#128272;','#a855f7','SSH HONEYPOT TRIGGERED','Remote access attempts are logged.'),
        'Port Scanner Honeypot':     ('&#128225;','#ff8800','PORT SCAN DETECTED','This endpoint is a honeypot for port scanners.'),
        'Honey Credentials Honeypot':('&#128273;','#ff0040','CREDENTIAL TRAP TRIGGERED','Accessing config/credential files is critical.'),
    }
    icon,color,title,desc = type_config.get(honeypot_type,('&#127855;','#ffaa00','HONEYPOT TRIGGERED','Decoy path accessed.'))
    return f"""<!DOCTYPE html><html><head><title>Honeypot</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Share Tech Mono',monospace;background:#050a05;display:flex;justify-content:center;align-items:center;height:100vh;cursor:crosshair;}}
body::after{{content:'';position:fixed;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.08) 2px,rgba(0,0,0,0.08) 4px);z-index:99;}}
.card{{background:#0c160c;border:1px solid {color};border-radius:4px;padding:50px 60px;text-align:center;max-width:540px;box-shadow:0 0 40px {color}33;position:relative;}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,{color},transparent);}}
.icon{{font-size:56px;margin-bottom:20px;}}
.badge{{display:inline-block;padding:4px 16px;border:1px solid {color};color:{color};font-size:9px;letter-spacing:3px;margin-bottom:16px;}}
h1{{font-family:'Orbitron',monospace;font-size:20px;color:{color};text-shadow:0 0 20px {color}88;margin-bottom:14px;letter-spacing:2px;}}
p{{color:rgba(0,255,65,0.4);font-size:12px;line-height:1.8;margin-bottom:8px;}}
.path{{color:{color};font-size:13px;margin:10px 0;}}
.ip{{color:rgba(0,255,65,0.5);font-size:11px;}}
.footer{{margin-top:24px;font-size:9px;color:rgba(0,255,65,0.2);letter-spacing:2px;}}
</style></head><body>
<div class="card">
  <div class="icon">{icon}</div>
  <div class="badge">{honeypot_type.upper()}</div>
  <h1>{title}</h1>
  <p>{desc}<br>Your activity has been logged and your IP flagged.</p>
  <div class="path">PATH: {path}</div>
  <div class="ip">IP: {ip}</div>
  <div class="footer">WEB APPLICATION INTRUSION PREVENTION SYSTEM</div>
</div></body></html>""", 403

# ── Main proxy ────────────────────────────────────────────────────────────────
@app.route('/', defaults={'path': ''}, methods=['GET','POST','PUT','DELETE','PATCH'])
@app.route('/<path:path>',            methods=['GET','POST','PUT','DELETE','PATCH'])
def proxy(path):
    ip = request.remote_addr

    # Reload from disk every request — admin unblock takes effect immediately
    blocked_ips, attack_count = load_blocked()

    # 1. Blocked IP?
    if ip in blocked_ips:
        print(f'[BLOCKED IP] {ip} tried /{path}')
        return ip_blocked_page(ip)

    # 2. Honeypot
    honeypot_type = is_honeypot('/' + path)
    if honeypot_type:
        print(f'[{honeypot_type.upper()}] {ip} hit /{path}')
        log_attack(ip, f'/{path}', 'Honeypot')
        attack_count[ip] = attack_count.get(ip, 0) + 1
        if attack_count[ip] >= 5:
            blocked_ips.add(ip)
        save_blocked(blocked_ips, attack_count)
        return honeypot_page(ip, '/' + path, honeypot_type)

    # 3. Rate limit
    if check_rate(ip):
        log_attack(ip, request.url, 'Rate Limit / DoS')
        return 'Too many requests.', 429

    # 4. Brute force
    if 'login' in path.lower() or 'login' in request.url.lower():
        if check_brute_force(ip):
            log_attack(ip, request.url, 'Brute Force')
            attack_count[ip] = attack_count.get(ip, 0) + 1
            if attack_count[ip] >= 5:
                blocked_ips.add(ip)
            save_blocked(blocked_ips, attack_count)
            return blocked_page(ip, 'Brute Force', 'HIGH')

    # 5. Payload detection
    payload = request.url + str(request.args) + str(request.data)
    attack_type = detect_attack(payload)

    if attack_type:
        from logger import SEVERITY_MAP
        severity = SEVERITY_MAP.get(attack_type, 'LOW')
        log_attack(ip, payload, attack_type)
        attack_count[ip] = attack_count.get(ip, 0) + 1
        print(f'[ATTACK] {ip} — {attack_type} [{severity}] count:{attack_count[ip]}')

        if attack_count[ip] >= 5:
            blocked_ips.add(ip)
            save_blocked(blocked_ips, attack_count)
            return ip_blocked_page(ip)

        save_blocked(blocked_ips, attack_count)
        return blocked_page(ip, attack_type, severity)

    # 6. Clean — forward to backend
    url = f'{TARGET}/{path}'
    resp = requests.request(
        method=request.method, url=url,
        params=request.args,
        headers={k: v for k, v in request.headers if k != 'Host'},
        data=request.get_data(), cookies=request.cookies,
        allow_redirects=False,
    )
    excluded = {'content-encoding','content-length','transfer-encoding','connection'}
    headers = [(n, v) for n, v in resp.raw.headers.items() if n.lower() not in excluded]
    return Response(resp.content, resp.status_code, headers)

if __name__ == '__main__':
    print('\n  WAF Proxy — Port 8080 | Block after 5 strikes\n')
    app.run(port=8080, debug=False)