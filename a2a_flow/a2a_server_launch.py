import subprocess
import os
import requests
import json
import time
import signal
from dotenv import load_dotenv

#------------------------------------------------------------------
# Load .env variables from the specified server directory
# NOTE: The path for load_dotenv needs to point to the file itself, 
#       not just the directory.
#------------------------------------------------------------------
load_dotenv(dotenv_path="./.env")

#------------------------------------------------------------------
# --- Configuration ---
A2A_SERVER_PATH = f"{os.path.expandvars('$HOME')}/projects/kaggle_genai_nov/a2a_flow/a2a_tutor_serv"
SERVER_HOST = "localhost"
SERVER_PORT = "8001"
AGENT_CARD_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/.well-known/agent-card.json"
MAX_ATTEMPTS = 30
POLL_INTERVAL_SECONDS = 2
# --- End Configuration ---

#------------------------------------------------------------------
# 1. Start A2A server
#------------------------------------------------------------------

print(f"🚀 Starting Eric Tutor A2A server in directory: {A2A_SERVER_PATH}")

server_process = subprocess.Popen(
    [
        "uvicorn",
        "agent:app",  # Module:app format (agent.py has the app)
        "--host",
        SERVER_HOST,
        "--port",
        SERVER_PORT,
        "--log-level", # Add log-level info to see Uvicorn startup messages in stdout
        "info",
    ],
    cwd=A2A_SERVER_PATH,  # Run from /server where the file is
    # Using PIPE for STDOUT/STDERR lets us capture and print them on failure
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ},  # Pass environment variables
    preexec_fn=os.setsid # Required for clean process group termination
)
globals()["eric_tutor_server_process"] = server_process


#------------------------------------------------------------------
# 2. Wait for server to start (poll until it responds)
#------------------------------------------------------------------
print("Polling for server readiness", end="", flush=True)

for attempt in range(MAX_ATTEMPTS):
    # Check if the process died *before* attempting the request
    if server_process.poll() is not None:
        print("\n\n❌ Subprocess died unexpectedly!")
        break
        
    try:
        response = requests.get(AGENT_CARD_URL, timeout=1)
        if response.status_code == 200:
            print(f"\n✅ Eric Tutor A2A server is running!")
            print(f"   Server URL: http://{SERVER_HOST}:{SERVER_PORT}")
            print(f"   Agent card: {AGENT_CARD_URL}")
            break
    except requests.exceptions.RequestException:
        time.sleep(POLL_INTERVAL_SECONDS)
        print(".", end="", flush=True)
else:
    # This block executes if the loop completed without 'break' (i.e., it timed out)
    print("\n\n⚠️  Server failed to become ready after maximum attempts.")


#------------------------------------------------------------------
# 3. Debugging and Cleanup
#------------------------------------------------------------------

# Read and print output for debugging, regardless of success/failure
try:
    # Use readlines() with a timeout if available, or just read the buffer now.
    # We use communicate() to get whatever is left in the buffer up to this point.
    stdout_output, stderr_output = server_process.communicate(timeout=1)
except subprocess.TimeoutExpired:
    # If the server is successfully running, communicate() will timeout
    # We still want to kill the process and print its initial logs
    stdout_output, stderr_output = server_process.stdout.read(), server_process.stderr.read()


print("\n--- Uvicorn STDOUT (Initial Logs) ---")
print(stdout_output.decode().strip() or "No initial stdout captured.")

print("\n--- Uvicorn STDERR (CRITICAL) ---")
# The error message from Uvicorn/Python will be here if it failed to start
error_message = stderr_output.decode().strip()
if error_message:
    print(error_message)
else:
    print("No errors reported on stderr.")


# Fetch the agent card if it successfully launched
if server_process.poll() is None and 'response' in locals() and response.status_code == 200:
    # The server is running and responded
    try:
        agent_card = response.json()
        print("\n📋 Eric Tutor Agent Card:")
        print(json.dumps(agent_card, indent=2))

        print("\n✨ Key Information:")
        print(f"   Name: {agent_card.get('name')}")
        print(f"   Description: {agent_card.get('description')}")
        print(f"   URL: {agent_card.get('url')}")
        print(f"   Skills: {len(agent_card.get('skills', []))} capabilities exposed")

    except Exception as e:
        print(f"\n❌ Error processing agent card: {e}")

# Keep server running until interrupted
if server_process.poll() is None:
    print(f"\n✅ Server running (PID: {server_process.pid})")
    print("\n💡 Press Ctrl+C to stop the server...\n")
    try:
        # Wait for the server process to complete (keeps it running)
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Eric Tutor server...")
        try:
            # Send SIGTERM to the process group to kill Uvicorn and its workers
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            server_process.wait(timeout=5)
            print("✅ Server stopped gracefully.")
        except Exception as e:
            print(f"⚠️  Error during shutdown: {e}. Forcing termination.")
            server_process.kill()
            print("❌ Server forcibly stopped.")
else:
    print("\n❌ Server failed to start. Check the error messages above.")