import re

# ── SQL Injection ─────────────────────────────────────────────────────────────
SQL_PATTERNS = [
    r"or\s+1=1", r"union\s+select", r"and\s+\d+=\d+",
    r"sleep\(", r"drop\s+table", r"insert\s+into",
    r"update\s+.*set", r"--", r"select\s+.*from",
    r"having\s+1=1", r"order\s+by\s+\d+", r"benchmark\(",
    r"waitfor\s+delay", r"xp_cmdshell", r"exec\s*\(",
]

# ── XSS ──────────────────────────────────────────────────────────────────────
XSS_PATTERNS = [
    r"<script", r"</script>", r"javascript:",
    r"onerror\s*=", r"onload\s*=", r"<iframe",
    r"alert\(", r"document\.cookie", r"onmouseover\s*=",
    r"eval\(", r"<svg", r"onkeyup\s*=", r"onfocus\s*=",
    r"<img.*onerror", r"expression\s*\(",
]

# ── Command Injection ─────────────────────────────────────────────────────────
COMMAND_INJECTION_PATTERNS = [
    r";\s*ls", r";\s*cat\s+", r";\s*rm\s+",
    r"\|\s*whoami", r"\|\s*net\s+user", r"&&\s*dir",
    r"`.*`", r"\$\(.*\)", r";\s*pwd",
    r"\|\s*id", r";\s*uname", r";\s*ifconfig",
    r";\s*wget\s+", r";\s*curl\s+",
]

# ── Path Traversal ────────────────────────────────────────────────────────────
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./", r"\.\.\\", r"%2e%2e%2f",
    r"%2e%2e/", r"etc/passwd", r"windows/system32",
    r"/etc/shadow", r"boot\.ini", r"proc/self",
    r"var/log", r"%252e%252e",
]

# ── CSRF ──────────────────────────────────────────────────────────────────────
CSRF_PATTERNS = [
    r"<form.*action\s*=\s*['\"]?https?://(?!localhost)",
    r"xmlhttprequest.*open\s*\(['\"]post",
    r"fetch\s*\(\s*['\"]https?://(?!localhost)",
    r"<img.*src\s*=\s*['\"]https?://.*\?.*=",
]

# ── XXE ───────────────────────────────────────────────────────────────────────
XXE_PATTERNS = [
    r"<!entity", r"<!doctype.*\[",
    r"system\s*['\"]http", r"file:///",
    r"php://filter", r"expect://",
]

# ── SSRF ──────────────────────────────────────────────────────────────────────
SSRF_PATTERNS = [
    r"file://",
    r"dict://",
    r"gopher://",
    r"http://169\.254\.169\.254",
    r"http://0\.0\.0\.0",
    r"http://\[::1\]",
]

# ── Header Injection ──────────────────────────────────────────────────────────
HEADER_INJECTION_PATTERNS = [
    r"%0d%0a", r"%0a%0d", r"\r\n",
    r"content-type:\s*text/html",
    r"location:\s*http",
]

# ── LDAP Injection ────────────────────────────────────────────────────────────
LDAP_PATTERNS = [
    r"\*\)\(", r"\)\(\|", r"objectclass=\*",
    r"\(\|\(uid=", r"admin\)\(",
]

ALL_PATTERNS = {
    'SQL Injection':        SQL_PATTERNS,
    'XSS':                  XSS_PATTERNS,
    'Command Injection':    COMMAND_INJECTION_PATTERNS,
    'Path Traversal':       PATH_TRAVERSAL_PATTERNS,
    'CSRF':                 CSRF_PATTERNS,
    'XXE':                  XXE_PATTERNS,
    'SSRF':                 SSRF_PATTERNS,
    'Header Injection':     HEADER_INJECTION_PATTERNS,
    'LDAP Injection':       LDAP_PATTERNS,
}

# ── HONEYPOT SYSTEM ───────────────────────────────────────────────────────────
# Each honeypot has a type, description and category for better logging

HONEYPOTS = {
    # 1. Web Login Honeypot — fake admin login pages
    'Web Login Honeypot': [
        '/admin', '/administrator', '/admin/login', '/admin-login',
        '/wp-admin', '/wp-login.php', '/cms/admin', '/panel',
        '/cpanel', '/webadmin', '/siteadmin', '/manage',
    ],

    # 2. Hidden URL Honeypot — hidden pages only bots/scanners find
    'Hidden URL Honeypot': [
        '/secret-admin', '/hidden', '/backup', '/old-admin',
        '/test', '/dev', '/staging', '/internal',
        '/private', '/restricted', '/confidential', '/vault',
    ],

    # 3. SSH / Service Honeypot — fake sensitive service endpoints
    'SSH Honeypot': [
        '/ssh', '/ssh-login', '/remote-access', '/shell',
        '/cmd', '/cmd.php', '/shell.php', '/exec',
        '/execute', '/terminal', '/console', '/bash',
    ],

    # 4. Open Port / Scanner Honeypot — common scanner targets
    'Port Scanner Honeypot': [
        '/phpmyadmin', '/pma', '/mysql', '/db', '/database',
        '/ftp', '/sftp', '/telnet', '/smtp', '/rdp',
        '/jenkins', '/solr', '/actuator', '/jmx', '/jboss',
    ],

    # 5. Honey Credentials / Config Honeypot — fake config and credential files
    'Honey Credentials Honeypot': [
        '/.env', '/.env.local', '/.env.production',
        '/config.php', '/config.json', '/settings.py',
        '/.git/config', '/.htpasswd', '/credentials.xml',
        '/web.config', '/wp-config.php', '/database.yml',
        '/secrets.json', '/api-keys.txt', '/passwords.txt',
        '/backup.sql', '/dump.sql', '/export.sql',
        '/xmlrpc.php',
    ],
}

# Flat list for fast lookup
_ALL_HONEYPOT_PATHS = {}
for htype, paths in HONEYPOTS.items():
    for p in paths:
        _ALL_HONEYPOT_PATHS[p.lower().rstrip('/')] = htype


def is_honeypot(path):
    """
    Returns the honeypot type string if the path is a trap, else None.
    """
    path_lower = path.lower().rstrip('/')
    # Exact match
    if path_lower in _ALL_HONEYPOT_PATHS:
        return _ALL_HONEYPOT_PATHS[path_lower]
    # Prefix match (e.g. /wp-admin/something)
    for trap_path, htype in _ALL_HONEYPOT_PATHS.items():
        if path_lower.startswith(trap_path + '/'):
            return htype
    return None


def detect_attack(payload):
    """
    Returns attack type string if malicious, None if clean.
    """
    payload_lower = payload.lower()
    for attack_type, patterns in ALL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, payload_lower):
                print(f'[{attack_type} DETECTED] pattern: {pattern}')
                return attack_type
    return None