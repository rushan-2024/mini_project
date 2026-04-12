# 🔥 Web Application Firewall - Intrusion Prevention System (WAF IPS)

A complete Python-based **Web Application Firewall (WAF)** with a full **Intrusion Prevention System**, dashboard, admin panel, simulator, and automated launcher for demonstration.

---

## 🚀 Features

* 🛡️ Rule-based HTTP request filtering
* 🔍 SQL Injection detection & blocking
* 📄 Attack logging system (`attacks.log`)
* ⚡ Rate limiting (DoS protection)
* 🌐 Proxy-based traffic monitoring
* 📊 Live attack dashboard
* 📑 PDF report generation
* 🔐 Admin panel with controls
* 🧪 Attack simulator + comparison mode
* 🎯 One-click execution using `start_demo.bat`

---

## 🧠 Architecture

Client → WAF Proxy (8080) → Backend Server (5001)

Additional Services:
- Dashboard (5002)
- Report Server (5003)
- Admin Panel (5004)
- Simulator & Stats (5005)

---

## 📁 Project Structure
backend.py # Vulnerable backend server
proxy.py # WAF proxy server
rules_engine.py # Attack detection logic
logger.py # Attack logging
rate_limiter.py # Rate limiting

dashboard.py # Live attack dashboard
report.py # PDF report generator
admin.py # Admin control panel
simulate.py # Attack simulator & comparison

setupdb.py # Database setup
start_demo.bat # 🔥 Master launcher (RUN THIS)

blocked_ips.json
attacks.log
test.db
requirements.txt
---

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/rushan-2024/mini_project.git
cd mini_project
2. Install Dependencies
pip install flask requests fpdf2
▶️ Run the Project (Recommended)
🔥 One-Click Start
start_demo.bat

✅ This will automatically:

Install dependencies
Setup database
Start all 6 servers
Open all pages in browser
🌐 Available Services
Service	URL
Home Page	http://localhost:5001

WAF Proxy Login	http://localhost:8080/login

Dashboard	http://localhost:5002

Report Generator	http://localhost:5003

Admin Panel	http://localhost:5004

Simulator	http://localhost:5005

Comparison	http://localhost:5005/compare

Project Stats	http://localhost:5005/stats

🔐 Admin Password: admin123

🧪 Testing Attacks
Example SQL Injection
/login?user=1 OR 1=1--
Expected Behavior
❌ Blocked (403)
📄 Logged in attacks.log
📊 Visible in dashboard
🔒 Detected Attacks
✔ SQL Injection (Basic & Time-based)
✔ SQL Comments (--)
✔ Dangerous Queries (DROP, INSERT, UPDATE)
✔ DoS (Rate limiting)
📊 Presentation Flow (IMPORTANT)
Home Page → http://localhost:5001
Project Stats → http://localhost:5005/stats
Simulator → http://localhost:5005
Compare WAF → http://localhost:5005/compare
Dashboard → http://localhost:5002
PDF Report → http://localhost:5003
Admin Panel → http://localhost:5004
⚠️ Limitations
Cannot detect advanced obfuscated attacks
Limited protection against XSS/CSRF
Basic rate limiting
🚀 Future Improvements
AI/ML-based attack detection
Advanced payload decoding
XSS & CSRF protection
IP banning & firewall rules
Cloud deployment
🛠 Tech Stack
Python
Flask
Requests
SQLite
FPDF (PDF Reports)
🤝 Contributing

Feel free to fork and contribute!