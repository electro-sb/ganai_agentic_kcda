from mcp.server.fastmcp import FastMCP
import sys
import sqlite3
import json
import os

DB_PATH = f"{os.path.expandvars("$HOME")}/projects/genai_nov_25/databases"
SQLITE_PATH = f"sqlite:///{DB_PATH}/my_agent_data.db"


def init_db(conn):
    # Initialize a default table if you want session-based persistence
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            data TEXT
        )
    """)
    conn.commit()

#-----------------------------------------
# database tool
#-----------------------------------------
@fastmcp.tool()
def sqlite_tool():
    """
    A tool to interact with a SQLite database. 
    This tool takes SQL queries as input from stdin, 
    executes them against a SQLite database, 
    and prints the results (for SELECT statements) or status (for other statements) to stdout in JSON format.
    """
    conn = sqlite3.connect(SQLITE_PATH)
    init_db(conn)
    cursor = conn.cursor()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            cursor.execute(line)
            if line.lower().startswith("select"):
                results = cursor.fetchall()
                print(json.dumps(results))
            else:
                conn.commit()
                print(json.dumps({"status": "success"}))
        except Exception as e:
            print(json.dumps({"error": str(e)}))
        sys.stdout.flush()

if __name__ == "__main__":
    fastmcp.run(transport='stdio')# Run the server in stdio mode    
