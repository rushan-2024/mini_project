@echo off
title WAF Intrusion Prevention System - Master Launcher
color 0a
cls
echo.
echo  ================================================================
echo  [         WEB APPLICATION FIREWALL - MAJOR PROJECT            ]
echo  [              SEM 4 -- MASTER LAUNCHER v2.0                  ]
echo  ================================================================
echo.
echo  Initializing all servers...
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Please install Python 3.
    pause
    exit /b 1
)

:: Install dependencies
echo  [SETUP] Checking dependencies...
pip install fpdf2 flask requests --quiet --disable-pip-version-check >nul 2>&1
echo  [OK]    Dependencies ready.
echo.

:: Setup database
echo  [INIT]  Setting up database...
python setupdb.py >nul 2>&1
echo  [OK]    Database ready.
echo.

:: 1. Backend Server
echo  [1/6]  Starting Backend Server         (Port 5001)...
start "BACKEND :5001" cmd /k "color 0a && echo [BACKEND :5001] && python backend.py"
timeout /t 1 /nobreak >nul

:: 2. WAF Proxy
echo  [2/6]  Starting WAF Proxy              (Port 8080)...
start "WAF PROXY :8080" cmd /k "color 0a && echo [WAF PROXY :8080] && python proxy.py"
timeout /t 1 /nobreak >nul

:: 3. Attack Dashboard
echo  [3/6]  Starting Attack Dashboard       (Port 5002)...
start "DASHBOARD :5002" cmd /k "color 0a && echo [DASHBOARD :5002] && python dashboard.py"
timeout /t 1 /nobreak >nul

:: 4. Report Server
echo  [4/6]  Starting PDF Report Server      (Port 5003)...
start "REPORT :5003" cmd /k "color 0a && echo [REPORT :5003] && python report.py"
timeout /t 1 /nobreak >nul

:: 5. Admin Panel
echo  [5/6]  Starting Admin Panel            (Port 5004)...
start "ADMIN :5004" cmd /k "color 0a && echo [ADMIN :5004] && python admin.py"
timeout /t 1 /nobreak >nul

:: 6. Simulator + Stats
echo  [6/6]  Starting Simulator + Stats      (Port 5005)...
start "SIMULATOR :5005" cmd /k "color 0a && echo [SIMULATOR :5005] && python simulate.py"
timeout /t 2 /nobreak >nul

cls
echo.
echo  ================================================================
echo  [                  ALL 6 SERVERS RUNNING!                     ]
echo  ================================================================
echo.
echo  Open these links in your browser:
echo.
echo    [1]  Home Page      -->  http://localhost:5001
echo    [2]  Dashboard      -->  http://localhost:5002
echo    [3]  Report + PDF   -->  http://localhost:5003
echo    [4]  Admin Panel    -->  http://localhost:5004  (pass: admin123)
echo    [5]  Simulator      -->  http://localhost:5005
echo    [6]  Comparison     -->  http://localhost:5005/compare
echo    [7]  Project Stats  -->  http://localhost:5005/stats
echo    [8]  WAF Demo Login -->  http://localhost:8080/login
echo.
echo  ----------------------------------------------------------------
echo  PRESENTATION ORDER:
echo    Step 1: http://localhost:5001        (Home page intro)
echo    Step 2: http://localhost:5005/stats  (Project stats)
echo    Step 3: http://localhost:5005        (Fire attacks live)
echo    Step 4: http://localhost:5005/compare (WAF on vs off)
echo    Step 5: http://localhost:5002        (Live dashboard)
echo    Step 6: http://localhost:5003        (Download PDF report)
echo    Step 7: http://localhost:5004        (Admin panel)
echo  ----------------------------------------------------------------
echo.
echo  Press any key to open all pages in browser automatically...
pause >nul

start "" "http://localhost:5001"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5002"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5003"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5004"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5005"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5005/compare"
timeout /t 1 /nobreak >nul
start "" "http://localhost:5005/stats"

echo.
echo  All pages opened! Ready for major project presentation.
echo  Press any key to exit launcher...
pause >nul