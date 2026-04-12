import re

# ── Pattern libraries ─────────────────────────────────────────────────────────

SQL_PATTERNS = [
    r"or\s+1=1", r"union\s+select", r"and\s+\d+=\d+",
    r"sleep\(", r"drop\s+table", r"insert\s+into",
    r"update\s+.*set", r"--", r"select\s+.*from",
    r"having\s+1=1", r"order\s+by\s+\d+", r"benchmark\(",
    r"waitfor\s+delay", r"xp_cmdshell", r"exec\s*\(",
]

XSS_PATTERNS = [
    r"<script", r"</script>", r"javascript:",
    r"onerror\s*=", r"onload\s*=", r"<iframe",
    r"alert\(", r"document\.cookie", r"onmouseover\s*=",
    r"eval\(", r"<svg", r"onkeyup\s*=", r"onfocus\s*=",
    r"<img.*onerror", r"expression\s*\(",
]

COMMAND_INJECTION_PATTERNS = [
    r";\s*ls", r";\s*cat\s+", r";\s*rm\s+",
    r"\|\s*whoami", r"\|\s*net\s+user", r"&&\s*dir",
    r"`.*`", r"\$\(.*\)", r";\s*pwd",
    r"\|\s*id", r";\s*uname", r";\s*ifconfig",
    r";\s*wget\s+", r";\s*curl\s+",
]

PATH_TRAVERSAL_PATTERNS = [
    r"\.\./", r"\.\.\\", r"%2e%2e%2f",
    r"%2e%2e/", r"etc/passwd", r"windows/system32",
    r"/etc/shadow", r"boot\.ini", r"proc/self",
    r"var/log", r"%252e%252e",
]

CSRF_PATTERNS = [
    r"<form.*action\s*=\s*['\"]?https?://(?!localhost)",
    r"xmlhttprequest.*open\s*\(['\"]post",
    r"fetch\s*\(\s*['\"]https?://(?!localhost)",
    r"axios\.(post|put|delete)\s*\(",
    r"<img.*src\s*=\s*['\"]https?://.*\?.*=",
]

XXE_PATTERNS = [
    r"<!entity", r"<!doctype.*\[",
    r"system\s*['\"]http", r"file:///",
    r"php://filter", r"expect://",
    r"<!element", r"&xxe;",
]

SSRF_PATTERNS = [
    r"file://",
    r"dict://",
    r"gopher://",
    r"http://169\.254\.169\.254",  # AWS metadata endpoint
    r"http://0\.0\.0\.0",
    r"http://\[::1\]",
]

HEADER_INJECTION_PATTERNS = [
    r"%0d%0a", r"%0a%0d", r"\r\n",
    r"content-type:\s*text/html",
    r"location:\s*http",
    r"%0d%0aset-cookie",
]

LDAP_PATTERNS = [
    r"\*\)\(", r"\)\(\|", r"objectclass=\*",
    r"\(\|\(uid=", r"admin\)\(",
    r"cn=\*", r"\*\)\(objectclass",
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

# ── Honeypot routes — any access = instant flag ───────────────────────────────
HONEYPOT_PATHS = [
    '/admin', '/administrator', '/wp-admin', '/wp-login.php',
    '/phpmyadmin', '/pma', '/.env', '/.git/config',
    '/config.php', '/backup', '/shell.php', '/cmd.php',
    '/console', '/manager', '/joomla', '/xmlrpc.php',
    '/api/v1/admin', '/actuator', '/solr', '/jenkins',
]

def is_honeypot(path):
    """Returns True if the path is a honeypot trap"""
    path_lower = path.lower().rstrip('/')
    for trap in HONEYPOT_PATHS:
        if path_lower == trap or path_lower.startswith(trap + '/'):
            return True
    return False

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