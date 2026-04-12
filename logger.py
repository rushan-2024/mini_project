import json
import time
import urllib.request

# ── Severity scoring per attack type ─────────────────────────────────────────
SEVERITY_MAP = {
    'SQL Injection':     'CRITICAL',
    'XSS':               'HIGH',
    'Command Injection': 'CRITICAL',
    'Path Traversal':    'HIGH',
    'XXE':               'HIGH',
    'CSRF':              'MEDIUM',
    'Brute Force':       'HIGH',
    'Honeypot':          'CRITICAL',
    'Unknown':           'LOW',
}

SEVERITY_SCORE = {
    'CRITICAL': 10,
    'HIGH':     7,
    'MEDIUM':   4,
    'LOW':      1,
}

def get_geoip(ip):
    """Fetch country/city info for an IP using free ip-api.com"""
    try:
        # Skip for localhost
        if ip in ('127.0.0.1', 'localhost', '::1'):
            return {'country': 'India', 'city': 'Mumbai', 'country_code': 'IN'}
        url = f'http://ip-api.com/json/{ip}?fields=country,city,countryCode'
        req = urllib.request.urlopen(url, timeout=2)
        data = json.loads(req.read().decode())
        return {
            'country':      data.get('country', 'Unknown'),
            'city':         data.get('city', 'Unknown'),
            'country_code': data.get('countryCode', '??'),
        }
    except:
        return {'country': 'Unknown', 'city': 'Unknown', 'country_code': '??'}

def log_attack(ip, payload, attack_type='Unknown'):
    severity = SEVERITY_MAP.get(attack_type, 'LOW')
    score    = SEVERITY_SCORE.get(severity, 1)
    geo      = get_geoip(ip)

    log = {
        'time':         time.ctime(),
        'ip':           ip,
        'attack_type':  attack_type,
        'severity':     severity,
        'score':        score,
        'payload':      payload,
        'country':      geo['country'],
        'city':         geo['city'],
        'country_code': geo['country_code'],
    }
    with open('attacks.log', 'a') as f:
        f.write(json.dumps(log) + '\n')
    print(f'[{severity}] {attack_type} from {ip} ({geo["country"]}) — score {score}')