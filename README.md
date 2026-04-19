🔥 Web Application Firewall - Intrusion Prevention System (WAF IPS)

A complete Python-based Web Application Firewall (WAF) integrated with an Intrusion Prevention System (IPS).
This project includes a unified backend UI, dashboard, admin panel, attack simulator, PDF reporting, and a one-click launcher for live demonstration.

🚀 Features
🛡️ Rule-based HTTP request filtering
🔍 SQL Injection detection & blocking
📄 Attack logging system (attacks.log)
⚡ Rate limiting (DoS protection)
🌐 Proxy-based traffic monitoring
📊 Live attack dashboard
📑 PDF report generation
🔐 Admin panel with controls
🧪 Attack simulator + comparison mode
🎯 One-click execution using start_demo.bat
🧠 Architecture
Client → WAF Proxy (8080) → Backend + UI Server (5001)
Active Services
Service	Port
Backend + UI	5001
WAF Proxy	8080
Dashboard (internal)	5001/dashboard
Report Server	5003
📁 Project Structure
backend.py        # Unified backend + UI (main app)
proxy.py          # WAF proxy server
rules_engine.py   # Attack detection logic
logger.py         # Attack logging
rate_limiter.py   # DoS protection

dashboard.py      # Attack dashboard (service)
report.py         # PDF report generator
admin.py          # Admin panel
simulate.py       # Attack simulator

setupdb.py        # Database setup
start_demo.bat    # 🔥 Master launcher (RUN THIS)

blocked_ips.json
attacks.log
test.db
requirements.txt
⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/rushan-2024/mini_project.git
cd mini_project
2️⃣ Install Dependencies
pip install flask requests fpdf2
▶️ Run the Project (Recommended)
🔥 One-Click Start
start_demo.bat
✅ What this script does:
✔ Checks Python installation
✔ Installs required dependencies
✔ Sets up SQLite database
✔ Starts all required servers:
Backend + UI (5001)
WAF Proxy (8080)
Dashboard (5002)
Report Server (5003)
✔ Automatically opens browser tabs
🌐 Application Routes (Unified UI)

All major features are accessible from one main server:

Feature	URL
Home Page	http://localhost:5001

Login Demo	http://localhost:5001/login

Dashboard	http://localhost:5001/dashboard

Simulator	http://localhost:5001/simulate

Comparison	http://localhost:5001/compare

Stats	http://localhost:5001/stats

Admin Panel	http://localhost:5001/admin

PDF Report	http://localhost:5003
🔐 Admin Credentials
Password: admin123
🧪 Testing Attacks
Example: SQL Injection
/login?user=1 OR 1=1--
✅ Expected Result
❌ Request blocked (HTTP 403)
📄 Entry added to attacks.log
📊 Visible in dashboard
🔒 Detected Attacks
✔ SQL Injection (Basic & Time-based)
✔ SQL Comments (--)
✔ Dangerous Queries (DROP, INSERT, UPDATE)
✔ DoS (Rate limiting)
📊 Presentation Flow (IMPORTANT)

Follow this order during demo:

/stats → Show project overview
/login → Demonstrate attack manually
/simulate → Trigger automated attacks
/compare → Show WAF ON vs OFF
/dashboard → View live attack logs
http://localhost:5003/download/pdf → Download report
/admin → Show admin controls
⚠️ Limitations
Limited detection of advanced obfuscated attacks
No full XSS/CSRF protection
Basic rate limiting
🚀 Future Improvements
AI/ML-based attack detection
Advanced payload decoding
XSS & CSRF protection
IP banning & firewall rules
Cloud deployment (AWS/Docker)
🛠 Tech Stack
Python
Flask
Requests
SQLite
FPDF2
🤝 Contributing

Contributions are welcome!

Fork the repo
Create a feature branch
Submit a pull request