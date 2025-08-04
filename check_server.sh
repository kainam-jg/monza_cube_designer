#!/bin/bash

# Check FastAPI XML File Server Status
# This script checks if the server is running

# Configuration
SERVER_NAME="monza_cube_designer"
PID_FILE="server.pid"
PORT=8000

echo "Checking $SERVER_NAME server status..."

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Server is not running (no PID file found)"
    exit 1
fi

# Read PID from file
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Server is running with PID $PID"
    echo "📁 PID file: $PID_FILE"
    echo "🌐 Server URL: http://localhost:$PORT"
    echo "📋 API docs: http://localhost:$PORT/docs"
    
    # Check if port is listening
    if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo "🔌 Port $PORT is listening"
    else
        echo "⚠️  Port $PORT is not listening (server may be starting up)"
    fi
    
    # Show last few lines of log
    if [ -f "logs/server.log" ]; then
        echo ""
        echo "📄 Recent log entries:"
        tail -5 "logs/server.log"
    fi
else
    echo "❌ Server is not running (PID $PID not found)"
    echo "🧹 Cleaning up stale PID file..."
    rm -f "$PID_FILE"
    exit 1
fi 