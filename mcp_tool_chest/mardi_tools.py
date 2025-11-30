from mcp.server.fastmcp import FastMCP
from mardi_search import MaRDIClient
import asyncio

mcp = FastMCP("mardi-search")
client = MaRDIClient()

@mcp.tool()
async def mardi_query(concept: str) -> str:
    """Search for mathematical formulas and definitions in MaRDI.
    
    Args:
        concept: The mathematical concept to search for (e.g., "gamma function").
    """
    return await client.filter_formulas_for_agent(concept)

if __name__ == "__main__":
    mcp.run(transport='stdio')
