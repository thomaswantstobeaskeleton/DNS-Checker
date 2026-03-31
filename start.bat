@echo off
setlocal EnableDelayedExpansion
title DNS Speed Test — Launcher
color 00

echo.
echo  ============================================================
echo    DNS Speed Test  ^|  Windows Launcher
echo  ============================================================
echo.

REM ── Check Python ─────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo.
    echo  Please install Python 3.8 or newer from:
    echo    https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% detected
echo.

REM ── Check pip ────────────────────────────────────────────────────────────────
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] pip is not available.
    echo  Try running:  python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)

REM ── Install / verify dependencies ────────────────────────────────────────────
set DEPS_FLAG=.deps_installed
set FORCE_REINSTALL=0

REM Allow forcing reinstall via argument:  start.bat --reinstall
if /i "%~1"=="--reinstall" (
    set FORCE_REINSTALL=1
    if exist "%DEPS_FLAG%" del "%DEPS_FLAG%"
    echo  [INFO] Forcing dependency reinstall...
    echo.
)

if not exist "%DEPS_FLAG%" (
    echo  [INFO] Installing required packages...
    echo         PyQt5 ^& dnspython
    echo.

    python -m pip install --upgrade pip --quiet

    python -m pip install "PyQt5>=5.15.0" --quiet
    if errorlevel 1 (
        echo  [ERROR] Failed to install PyQt5.
        echo  Try manually:  pip install PyQt5
        echo.
        pause
        exit /b 1
    )

    python -m pip install "dnspython>=2.3.0" --quiet
    if errorlevel 1 (
        echo  [WARN] dnspython install failed — app will use socket fallback.
        echo.
    )

    REM Write marker so we skip install next time
    echo Installed on %date% %time% > "%DEPS_FLAG%"
    echo  [OK] Dependencies installed successfully.
    echo.
) else (
    echo  [OK] Dependencies already installed. (run with --reinstall to force)
    echo.
)

REM ── Check if dns_servers.txt exists, create default if missing ────────────────
if not exist "dns_servers.txt" (
    echo  [INFO] dns_servers.txt not found — creating default list...
    (
        echo # DNS Servers List
        echo # Format: IP, Provider, Category
        echo # Lines starting with # are comments
        echo.
        echo # ── Global Providers ──────────────────────────────────────
        echo 1.1.1.1, Cloudflare, Global
        echo 1.0.0.1, Cloudflare, Global
        echo 8.8.8.8, Google, Global
        echo 8.8.4.4, Google, Global
        echo 9.9.9.9, Quad9, Global
        echo 149.112.112.112, Quad9, Global
        echo 208.67.222.222, OpenDNS, Global
        echo 208.67.220.220, OpenDNS, Global
        echo 94.140.14.14, AdGuard, Global
        echo 94.140.15.15, AdGuard, Global
        echo 76.76.19.19, Alternate DNS, Global
        echo 76.223.122.150, Alternate DNS, Global
        echo 185.228.168.168, CleanBrowsing, Global
        echo 185.228.169.168, CleanBrowsing, Global
        echo 84.200.69.80, DNS.WATCH, Global
        echo 84.200.70.40, DNS.WATCH, Global
        echo 4.2.2.1, Level3, Global
        echo 4.2.2.2, Level3, Global
        echo 4.2.2.3, Level3, Global
        echo 4.2.2.4, Level3, Global
        echo 64.6.64.6, Verisign, Global
        echo 64.6.65.6, Verisign, Global
        echo 77.88.8.8, Yandex, Global
        echo 77.88.8.1, Yandex, Global
        echo 77.88.8.2, Yandex Safe, Global
        echo 77.88.8.3, Yandex Safe, Global
        echo 80.80.80.80, Freenom, Global
        echo 80.80.81.81, Freenom, Global
        echo 199.85.126.10, Norton, Global
        echo 199.85.127.10, Norton, Global
        echo 156.154.70.1, Neustar, Global
        echo 156.154.71.1, Neustar, Global
        echo 45.90.28.0, NextDNS, Global
        echo 45.90.30.0, NextDNS, Global
        echo 194.242.2.2, Mullvad, Global
        echo 194.242.2.3, Mullvad, Global
        echo 8.26.56.26, Comodo, Global
        echo 8.20.247.20, Comodo, Global
        echo 195.46.39.39, SafeDNS, Global
        echo 195.46.39.40, SafeDNS, Global
        echo 74.82.42.42, Hurricane Electric, Global
        echo 193.110.81.0, dns0.eu, Global
        echo 185.253.5.0, dns0.eu, Global
        echo 176.103.130.130, AdGuard Alt, Global
        echo 176.103.130.131, AdGuard Alt, Global
        echo.
        echo # ── Iran Providers ────────────────────────────────────────
        echo 10.202.10.10, Shecan, Iran
        echo 10.202.10.11, Shecan, Iran
        echo 10.202.10.102, Shecan Alt, Iran
        echo 10.202.10.202, Shecan Alt, Iran
        echo 178.22.122.100, Electro, Iran
        echo 185.51.200.2, Radar, Iran
        echo 185.55.224.24, 403, Iran
        echo 185.55.225.25, 403, Iran
        echo 185.55.226.26, 403, Iran
        echo 78.157.42.100, Begzar, Iran
        echo 78.157.42.101, Begzar, Iran
        echo 188.75.80.80, Shatel, Iran
        echo 188.75.90.90, Shatel, Iran
        echo 194.36.174.1, PIR DNS, Iran
        echo 194.36.174.2, PIR DNS, Iran
        echo 5.202.100.100, Pars Online, Iran
        echo 5.202.100.101, Pars Online, Iran
        echo 185.141.168.130, Host Iran, Iran
        echo 185.141.168.131, Host Iran, Iran
        echo 89.237.98.12, Fanap, Iran
        echo 89.237.110.12, Fanap, Iran
        echo 83.147.192.100, Arvan, Iran
        echo 83.147.193.100, Arvan, Iran
        echo 83.147.194.100, Arvan, Iran
        echo 83.147.195.100, Arvan, Iran
    ) > dns_servers.txt
    echo  [OK] dns_servers.txt created.
    echo.
)

REM ── Admin detection ───────────────────────────────────────────────────────────
net session >nul 2>&1
if errorlevel 1 (
    echo  [WARN] Not running as Administrator.
    echo         DNS testing works normally, but applying DNS to
    echo         your adapter will require Administrator privileges.
    echo.
    echo  To apply DNS settings, right-click start.bat and choose
    echo  "Run as administrator".
    echo.
) else (
    echo  [OK] Running as Administrator — all features available.
    echo.
)

REM ── Launch application ────────────────────────────────────────────────────────
echo  Starting DNS Speed Test...
echo  ============================================================
echo.

python dns_speed_test.py %*

set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo.
    echo  ============================================================
    echo  [ERROR] Application exited with code %EXIT_CODE%.
    echo.
    echo  Common fixes:
    echo    - Run:  start.bat --reinstall     (reinstall dependencies)
    echo    - Run:  pip install PyQt5 dnspython
    echo    - Make sure dns_speed_test.py is in the same folder
    echo  ============================================================
    echo.
    pause
)

endlocal
exit /b %EXIT_CODE%
