import time

# ── General rate limiting ─────────────────────────────────────────────────────
request_counts = {}          # ip -> count
request_window = {}          # ip -> window_start_time
RATE_LIMIT     = 100         # max requests per window
WINDOW_SECONDS = 60          # window duration in seconds

# ── Brute force detection ─────────────────────────────────────────────────────
login_attempts  = {}         # ip -> list of timestamps
BRUTE_THRESHOLD = 5          # max login attempts
BRUTE_WINDOW    = 60         # within this many seconds

def check_rate(ip):
    """
    Returns True if IP exceeds general rate limit.
    Resets count every WINDOW_SECONDS seconds.
    """
    now = time.time()
    if ip not in request_window:
        request_window[ip] = now
        request_counts[ip] = 0

    # Reset window if expired
    if now - request_window[ip] > WINDOW_SECONDS:
        request_window[ip] = now
        request_counts[ip] = 0

    request_counts[ip] += 1
    if request_counts[ip] > RATE_LIMIT:
        print(f'[RATE LIMIT] {ip} exceeded {RATE_LIMIT} requests in {WINDOW_SECONDS}s')
        return True
    return False

def check_brute_force(ip):
    """
    Returns True if IP has made more than BRUTE_THRESHOLD
    login attempts within BRUTE_WINDOW seconds.
    """
    now = time.time()
    if ip not in login_attempts:
        login_attempts[ip] = []

    # Keep only recent attempts within the window
    login_attempts[ip] = [t for t in login_attempts[ip] if now - t < BRUTE_WINDOW]
    login_attempts[ip].append(now)

    count = len(login_attempts[ip])
    if count > BRUTE_THRESHOLD:
        print(f'[BRUTE FORCE] {ip} — {count} login attempts in {BRUTE_WINDOW}s')
        return True
    return False