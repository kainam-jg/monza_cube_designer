#!/bin/bash

# Stop FastAPI XML File Server
# This script stops the server using the PID file

# Configuration
SERVER_NAME="monza_cube_designer"
PID_FILE="server.pid"

echo "Stopping $SERVER_NAME server..."

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "PID file not found. Server may not be running."
    exit 1
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p $PID > /dev/null 2>&1; then
    echo "Server is not running (PID $PID not found)"
    rm -f "$PID_FILE"
    exit 1
fi

# Kill the process
echo "Killing server process with PID $PID..."
kill $PID

# Wait a moment for the process to terminate
sleep 2

# Check if process was killed
if ps -p $PID > /dev/null 2>&1; then
    echo "Server is still running. Force killing..."
    kill -9 $PID
    sleep 1
fi

# Remove PID file
rm -f "$PID_FILE"

echo "Server stopped successfully"
echo "Log file: logs/server.log" 