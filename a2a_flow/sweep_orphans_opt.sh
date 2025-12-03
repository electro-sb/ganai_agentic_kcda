#!/bin/bash
# 
# Script to forcefully stop the process running on the specified port (default 8001).

# --- Configuration ---
SERVER_PORT=${1:-8001}
echo "Attempting to stop server running on port $SERVER_PORT..."
# --- End Configuration ---


# Use 'lsof' to find the Process ID (PID) listening on the port
# -t: output PIDs only
# -i: Internet address format (TCP)
PID=$(lsof -t -i tcp:"$SERVER_PORT")

if [ -z "$PID" ]; then
    echo "✅ No process found listening on port $SERVER_PORT. Server is already stopped."
else
    # Check if the PID is actually a process group ID (often the case with Uvicorn/Gunicorn)
    # If the process was started with os.setsid, killing the PID is sufficient,
    # but to be extra sure, we can target the whole process group if needed.
    
    echo "Found PID(s): $PID"
    
    # Send SIGTERM (graceful shutdown) first
    kill "$PID"
    sleep 2
    
    # Check if the process is still running. If so, kill forcefully with SIGKILL.
    if ps -p "$PID" > /dev/null; then
        echo "Process did not terminate gracefully. Forcibly killing PID(s): $PID"
        kill -9 "$PID"
        echo "❌ Server forcibly stopped."
    else
        echo "✅ Server gracefully stopped."
    fi
fi

# Exit with success status
exit 0