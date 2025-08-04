@echo off
REM Stop FastAPI XML File Server
REM This script stops the server using the PID file

REM Configuration
set SERVER_NAME=monza_cube_designer
set PID_FILE=server.pid

echo Stopping %SERVER_NAME% server...

REM Check if PID file exists
if not exist "%PID_FILE%" (
    echo PID file not found. Server may not be running.
    exit /b 1
)

REM Read PID from file
for /f "tokens=*" %%i in (%PID_FILE%) do set PID=%%i

REM Check if process is running
tasklist /FI "PID eq !PID!" 2>NUL | find /I "python.exe" >NUL
if errorlevel 1 (
    echo Server is not running (PID !PID! not found)
    del "%PID_FILE%"
    exit /b 1
)

REM Kill the process
echo Killing server process with PID !PID!...
taskkill /PID !PID! /F

REM Wait a moment for the process to terminate
timeout /t 2 /nobreak >NUL

REM Check if process was killed
tasklist /FI "PID eq !PID!" 2>NUL | find /I "python.exe" >NUL
if not errorlevel 1 (
    echo Server is still running. Force killing...
    taskkill /PID !PID! /F
    timeout /t 1 /nobreak >NUL
)

REM Remove PID file
del "%PID_FILE%"

echo Server stopped successfully
echo Log file: logs\server.log 