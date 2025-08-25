#!/bin/bash

# Start FastAPI XML File Server
# This script starts the server in the background and logs output

# Configuration
SERVER_NAME="monza_cube_designer"
LOG_FILE="server.log"
PID_FILE="server.pid"
PORT=8000

echo "Starting $SERVER_NAME server..."

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Server is already running with PID $PID"
        exit 1
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Create log directory if it doesn't exist
mkdir -p logs

# Activate virtual environment
source /opt/tomcat/.venv/bin/activate

# Start the server with nohup
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "logs/$LOG_FILE" 2>&1 &

# Save the PID
echo $! > "$PID_FILE"

echo "Server started with PID $!"
echo "Log file: logs/$LOG_FILE"
echo "PID file: $PID_FILE"
echo "Server will be available at: http://localhost:$PORT"
echo ""
echo "To check server status: ./check_server.sh"
echo "To stop server: ./stop_server.sh" 