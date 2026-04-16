@echo off
title WAF IPS - Master Launcher
color 0a
cls
echo.
echo  ================================================================
echo  [         WEB APPLICATION IPS - MAJOR PROJECT                 ]
echo  [              SEM 4 -- MASTER LAUNCHER v3.0                  ]
echo  ================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (echo  [ERROR] Python not found. & pause & exit /b 1)

echo  [SETUP] Installing dependencies...
pip install fpdf2 flask requests --quiet --disable-pip-version-check >nul 2>&1
echo  [OK]    Done.
echo.
echo  [INIT]  Setting up database...
python setupdb.py >nul 2>&1
echo  [OK]    Database ready.
echo.

echo  [1/4]  Starting Unified Backend App    (Port 5001)...
start "BACKEND+UI :5001" cmd /k "color 0a && python backend.py"
timeout /t 1 /nobreak >nul

echo  [2/4]  Starting WAF Proxy              (Port 8080)...
start "WAF PROXY :8080" cmd /k "color 0a && python proxy.py"
timeout /t 1 /nobreak >nul

echo  [3/4]  Starting Attack Dashboard       (Port 5002)...
start "DASHBOARD :5002" cmd /k "color 0a && python dashboard.py"
timeout /t 1 /nobreak >nul

echo  [4/4]  Starting PDF Report Server      (Port 5003)...
start "REPORT :5003" cmd /k "color 0a && python report.py"
timeout /t 2 /nobreak >nul

cls
echo.
echo  ================================================================
echo  [                  ALL SERVERS RUNNING!                       ]
echo  ================================================================
echo.
echo  ALL PAGES (navigate from home):
echo.
echo    Home Page    -->  http://localhost:5001
echo    Demo Login   -->  http://localhost:5001/login
echo    Dashboard    -->  http://localhost:5001/dashboard
echo    Simulator    -->  http://localhost:5001/simulate
echo    Comparison   -->  http://localhost:5001/compare
echo    Stats        -->  http://localhost:5001/stats
echo    Admin Panel  -->  http://localhost:5001/admin
echo    Report+PDF   -->  http://localhost:5003
echo.
echo  ----------------------------------------------------------------
echo  PRESENTATION ORDER:
echo    Step 1: /stats      Show project overview
echo    Step 2: /login      Demo attacks live
echo    Step 3: /simulate   Fire all attacks at once
echo    Step 4: /compare    WAF on vs off demo
echo    Step 5: /dashboard  Show live attack log
echo    Step 6: 5003/download/pdf  Download PDF report
echo    Step 7: /admin      Show management panel
echo  ----------------------------------------------------------------
echo.
echo  Press any key to open browser...
pause >nul

start "" "http://localhost:5001"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5001/dashboard"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5001/simulate"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5001/compare"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5001/stats"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5003"

echo  Done! Press any key to exit.
pause >nul