from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()
fastmcp = FastMCP("wolfram-llm")
API_KEY = os.getenv("WOLFRAM_API_KEY")

@fastmcp.tool()
def wolfram_query(query: str) -> str:
    """Query Wolfram Alpha LLM API for computational answers.
    
    Args:
        query: The input query string to ask Wolfram Alpha
        
    Returns:
        Computational answer string
    """
    if not API_KEY:
        return "Error: WOLFRAM_API_KEY missing"
    
    url = "https://www.wolframalpha.com/api/v1/llm-api"
    params = {"input": query, "appid": API_KEY}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        # print(f"DEBUG: Status={resp.status_code}, Content-Type={resp.headers.get('content-type')}")
        # print(f"DEBUG: Response={resp.text[:200]}")  # First 200 chars
        resp.raise_for_status()
        
        # Wolfram LLM API returns plain text, NOT JSON
        return resp.text if resp.text else "No result from Wolfram"
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    fastmcp.run(transport='stdio')
