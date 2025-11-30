from mcp.server.fastmcp import FastMCP
from ddgs import DDGS
import json

fastmcp = FastMCP("duckduckgo-search")

@fastmcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """
    Performs a web search using DuckDuckGo.
    
    Args:
        query: The search query.
        max_results: The maximum number of results to return (default: 5).
        
    Returns:
        A formatted string containing the search results with title, link, and snippet.
    """
    try:
        # Perform the search
        results = DDGS().text(query, max_results=max_results)
        
        if not results:
            return "No search results found. The query may have been blocked or returned no results."
        
        # Format results in a more readable way
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""Result {i}:
Title: {result.get('title', 'N/A')}
Link: {result.get('href', 'N/A')}
Snippet: {result.get('body', 'N/A')}
"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error performing search: {str(e)}"

if __name__ == "__main__":
    fastmcp.run(transport='stdio')
