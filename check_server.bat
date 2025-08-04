@echo off
REM Check FastAPI XML File Server Status
REM This script checks if the server is running

REM Configuration
set SERVER_NAME=monza_cube_designer
set PID_FILE=server.pid
set PORT=8000

echo Checking %SERVER_NAME% server status...

REM Check if PID file exists
if not exist "%PID_FILE%" (
    echo ❌ Server is not running (no PID file found)
    exit /b 1
)

REM Read PID from file
for /f "tokens=*" %%i in (%PID_FILE%) do set PID=%%i

REM Check if process is running
tasklist /FI "PID eq !PID!" 2>NUL | find /I "python.exe" >NUL
if not errorlevel 1 (
    echo ✅ Server is running with PID !PID!
    echo 📁 PID file: %PID_FILE%
    echo 🌐 Server URL: http://localhost:%PORT%
    echo 📋 API docs: http://localhost:%PORT%/docs
    
    REM Check if port is listening
    netstat -an | find ":%PORT% " >NUL
    if not errorlevel 1 (
        echo 🔌 Port %PORT% is listening
    ) else (
        echo ⚠️  Port %PORT% is not listening (server may be starting up)
    )
    
    REM Show last few lines of log
    if exist "logs\server.log" (
        echo.
        echo 📄 Recent log entries:
        powershell "Get-Content 'logs\server.log' | Select-Object -Last 5"
    )
) else (
    echo ❌ Server is not running (PID !PID! not found)
    echo 🧹 Cleaning up stale PID file...
    del "%PID_FILE%"
    exit /b 1
) 