🔥 Web Application Firewall - Intrusion Prevention System (WAF IPS)

A complete Python-based Web Application Firewall (WAF) integrated with an Intrusion Prevention System (IPS).
Includes a unified UI, dashboard, admin panel, attack simulator, PDF reporting, and a one-click launcher for demo.

🚀 Features
Rule-based HTTP request filtering
SQL Injection detection & blocking
Attack logging system (attacks.log)
Rate limiting (DoS protection)
Proxy-based traffic monitoring
Live attack dashboard
PDF report generation
Admin panel with controls
Attack simulator + comparison mode
One-click execution using start_demo.bat
🧠 Architecture
Client → WAF Proxy (8080) → Backend + UI Server (5001)
📁 Project Structure
backend.py        # Unified backend + UI
proxy.py          # WAF proxy server
rules_engine.py   # Detection logic
logger.py         # Logging system
rate_limiter.py   # Rate limiting

dashboard.py      # Dashboard service
report.py         # PDF generator
admin.py          # Admin panel
simulate.py       # Attack simulator

setupdb.py        # Database setup
start_demo.bat    # Master launcher

blocked_ips.json
attacks.log
test.db
requirements.txt
⚙️ Installation
Clone Repository
git clone https://github.com/rushan-2024/mini_project.git
cd mini_project
Install Dependencies
pip install flask requests fpdf2
▶️ Run the Project
One-Click Start
start_demo.bat
What it does:
Installs dependencies
Sets up database
Starts all servers
Opens browser automatically
🌐 Application Routes
Feature	URL
Home	http://localhost:5001

Login	http://localhost:5001/login

Dashboard	http://localhost:5001/dashboard

Simulator	http://localhost:5001/simulate

Comparison	http://localhost:5001/compare

Stats	http://localhost:5001/stats

Admin Panel	http://localhost:5001/admin

PDF Report	http://localhost:5003
🔐 Admin Credentials
Password: admin123
🧪 Testing Attacks
SQL Injection Example
/login?user=1 OR 1=1--
Expected Result
Request blocked (403)
Logged in attacks.log
Visible in dashboard
🔒 Detected Attacks
SQL Injection (basic & time-based)
SQL comments (--)
Dangerous queries (DROP, INSERT, UPDATE)
DoS via rate limiting
📊 Demo Flow (Important)

Follow this sequence:

/stats → Project overview
/login → Manual attack
/simulate → Automated attacks
/compare → WAF ON vs OFF
/dashboard → Live logs
http://localhost:5003/download/pdf → Download report
/admin → Admin panel
⚠️ Limitations
Cannot detect advanced obfuscated attacks
Limited XSS/CSRF protection
Basic rate limiting
🚀 Future Improvements
AI/ML-based detection
Advanced payload decoding
XSS & CSRF protection
IP banning system
Cloud deployment (Docker/AWS)
🛠 Tech Stack
Python
Flask
Requests
SQLite
FPDF2
🤝 Contributing
Fork the repository
Create a branch
Submit a pull request
📜 License

For educational and academic use.
