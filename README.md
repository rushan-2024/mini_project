# 🔥 Web Firewall Detection (Python WAF)

A Python-based smart Web Application Firewall (WAF) that detects, blocks, and logs malicious HTTP traffic, including SQL injection attacks, using rule-based filtering and proxy analysis.

---

## 🚀 Features

* 🛡️ Rule-based filtering of HTTP requests
* 🔍 SQL injection detection
* 📄 Attack logging (`attacks.log`)
* ⚡ Rate limiting (basic DoS protection)
* 🌐 Proxy-based traffic monitoring

---

## 🧠 Architecture

Client → WAF Proxy (Port 8080) → Backend Server (Port 5001)

* Requests first pass through the firewall
* Firewall checks for malicious patterns
* Safe requests are forwarded to backend
* Malicious requests are blocked and logged

---

## 📁 Project Structure

```
backend.py         # Vulnerable backend server
proxy.py           # WAF proxy server
rules_engine.py    # Attack detection logic
logger.py          # Logs detected attacks
rate_limiter.py    # Rate limiting logic
test.db            # SQLite database
requirements.txt
```

---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone https://github.com/anujatappeta/web_firewall_detection.git
cd web_firewall_detection
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Setup database

```bash
python setupdb.py
```

---

## ▶️ Running the Project

### 🔹 Step 1: Start backend server

```bash
python backend.py
```

Runs on: `http://localhost:5001`

---

### 🔹 Step 2: Start firewall proxy

```bash
python proxy.py
```

Runs on: `http://localhost:8080`

---

## 🔒 Detected Attacks

The firewall currently detects and blocks:

* ✔ Basic SQL Injection

  * `OR 1=1`, `AND 1=1`, `UNION SELECT`

* ✔ SQL Comment Injection

  * `--`

* ✔ Dangerous SQL Commands

  * `DROP TABLE`, `INSERT INTO`, `UPDATE ... SET`

* ✔ Time-based SQL Injection

  * `SLEEP()`

* ✔ Basic DoS Attacks

  * Excessive requests from same IP

---

## 🧪 Testing Attacks (IMPORTANT)

To test SQL injection attacks, install **sqlmap**:

### 🔹 Install sqlmap

```bash
git clone https://github.com/sqlmapproject/sqlmap.git
cd sqlmap
```

---

### 🔹 Run attack test

```bash
python sqlmap.py -u "http://localhost:8080/login?user=1"
```

---

### 🔥 Example Attack Payload

```http
/login?user=1 OR 1=1--
```

---

### ✅ Expected Behavior

* Malicious request → ❌ Blocked (403)
* Attack logged → `attacks.log`

---

## 📄 Logging Example

```json
{
  "time": "Mon Mar 17",
  "ip": "127.0.0.1",
  "payload": "/login?user=1 OR 1=1--"
}
```

---

## ⚠️ Limitations

* Does not yet detect encoded or obfuscated payloads
* Cannot handle advanced evasion techniques

---

## 🚀 Future Improvements

* Detect advanced SQL injection evasion techniques used by sqlmap tamper scripts (encoding, obfuscation, payload mutation)
* Machine learning-based anomaly detection
* Web dashboard for monitoring logs
* Advanced rate limiting and IP blocking
* Support for XSS, CSRF, and command injection

---

## 🛠 Tech Stack

* Python
* Flask
* Requests
* SQLite

---

## 🤝 Contributing

Feel free to fork the repository and submit pull requests.

---

## 📜 License

MIT License
