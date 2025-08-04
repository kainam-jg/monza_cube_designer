@echo off
REM Start FastAPI XML File Server
REM This script starts the server in the background and logs output

REM Configuration
set SERVER_NAME=monza_cube_designer
set LOG_FILE=server.log
set PID_FILE=server.pid
set PORT=8000

echo Starting %SERVER_NAME% server...

REM Check if server is already running
if exist "%PID_FILE%" (
    for /f "tokens=*" %%i in (%PID_FILE%) do set PID=%%i
    tasklist /FI "PID eq !PID!" 2>NUL | find /I "python.exe" >NUL
    if not errorlevel 1 (
        echo Server is already running with PID !PID!
        exit /b 1
    ) else (
        echo Removing stale PID file
        del "%PID_FILE%"
    )
)

REM Create log directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start the server
echo Starting server...
start /B python main.py > "logs\%LOG_FILE%" 2>&1

REM Get the PID of the last started process
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| find "python.exe"') do set PID=%%a

REM Save the PID (remove quotes)
set PID=!PID:"=!

REM Save PID to file
echo !PID! > "%PID_FILE%"

echo Server started with PID !PID!
echo Log file: logs\%LOG_FILE%
echo PID file: %PID_FILE%
echo Server will be available at: http://localhost:%PORT%
echo.
echo To check server status: check_server.bat
echo To stop server: stop_server.bat

pause 