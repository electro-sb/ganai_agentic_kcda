import uuid
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool

#from agent_dev_kit.mcp.toolset import ToolboxHttpConnectionParams

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="./.env")

#------------------------------------------------------------------
# Agentic Workflow description
#------------------------------------------------------------------
"""
This is a math tutor agent that helps users with solving math problems.
It uses a root agent to coordinate the subagents.

1. The Root/Manager (Orchestrator): 
    Role: The user's main contact. It breaks down the query and synthesizes the answer.
    Tools: web_search_agent, wolfram_agent, mardi agent

2. The Archivist (MaRDI Agent): 
    Role: Interprets the sparse MaRDI output.
    tools: mardi_query(mcp tool)

3. The Analyst (Wolfram Agent):
    Role: Solves the math problem.
    tools: wolfram_query(mcp tool)

4. The Calculator (Trivial calculation agent):
    Role: Solves trivial arithmatic problems.
    tools: add, subtract, multiply, divide(mcp tool)

5. The Web Search Agent:
    Role: Looks up information on the web.
    tools: google_search
"""


#------------------------------------------------------------------
# Retry function
#------------------------------------------------------------------
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)


#------------------------------------------------------------------
# MCP Toolset
#------------------------------------------------------------------
WOLFRAM_MCP_SERVER = f"{os.path.expandvars('$HOME')}/projects/kaggle_genai_nov/mcp_tool_chest/wolfram_tools.py"
MARDI_MCP_SERVER = f"{os.path.expandvars('$HOME')}/projects/kaggle_genai_nov/mcp_tool_chest/mardi_tools.py"
CALCULATOR_MCP_SERVER = f"{os.path.expandvars('$HOME')}/projects/kaggle_genai_nov/mcp_tool_chest/calculator.py"
DUCKDUCKGO_MCP_SERVER = f"{os.path.expandvars('$HOME')}/projects/kaggle_genai_nov/mcp_tool_chest/duckduckgo_tools.py"
#------------------------------------------------------------------
# Wolfram MCP toolset wrapper
#------------------------------------------------------------------
mcp_wolfram = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",  # Run MCP server via python
            args=[
                "-u",
                WOLFRAM_MCP_SERVER,
            ],
            tool_filter=["wolfram_query"],
        ),
        timeout=60,
    )
)
#------------------------------------------------------------------
# MaRDI MCP toolset wrapper
#------------------------------------------------------------------
mcp_mardi = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[
                "-u",
                MARDI_MCP_SERVER,
            ],
            tool_filter=["mardi_query"],
        ),
        timeout=60,
    )
)
#------------------------------------------------------------------
# Calculator MCP toolset wrapper
#------------------------------------------------------------------
mcp_calculator = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[
                "-u",
                CALCULATOR_MCP_SERVER,
            ],
            tool_filter=["add", "subtract", "multiply", "divide", "power", "sqrt"],
        ),
        timeout=60,
    )
)
#------------------------------------------------------------------
# DuckDuckGo MCP toolset wrapper
#------------------------------------------------------------------
mcp_duckduckgo = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[
                "-u",
                DUCKDUCKGO_MCP_SERVER,
            ],
            tool_filter=["web_search"],
        ),
        timeout=60,
    )
)
#-----------------------------------------------------------------
# Read Prompts
#-----------------------------------------------------------------
with open("./tutor_agent/prompts/wolfram_prompt.md", "r") as f:
    wolfram_prompt = f.read()

with open("./tutor_agent/prompts/mardi_prompt.md", "r") as f:
    mardi_prompt = f.read()

with open("./tutor_agent/prompts/orchastrator_prompt.md", "r") as f:
    root_prompt = f.read()

#-----------------------------------------------------------------
# Wolfram Agent : Solver/ Analyst
#-----------------------------------------------------------------
wolfram_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),#flash-lite doesn't support function calling
    name="wolfram_agent",
    instruction=f"""
    {wolfram_prompt}
    """,
    tools=[mcp_wolfram], #mcp_wolfram_server,
)

#-----------------------------------------------------------------
# MaRDI Agent : The Archivist 
#-----------------------------------------------------------------
mardi_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="mardi_agent",
    instruction=f"""
    {mardi_prompt}
    """,
    tools=[mcp_mardi],
)

#-----------------------------------------------------------------
# Calculator Agent : The Trivial Calculator
#-----------------------------------------------------------------
calculator_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="calculator_agent",
    instruction="""
    You are a calculator agent.
    Use the provided tools to perform basic arithmetic operations.
    """,
    tools=[mcp_calculator],
)

#------------------------------------------------------------------
# Web Search Agent : The Web Searcher
#------------------------------------------------------------------
web_search_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),#flash-lite doesn't support function calling
    name="web_search_agent",
    instruction=f"""
    You are a web search agent.
    Your primary role is to find **current information** such as:
    - Current time and date in specific locations.
    - Weather forecasts and conditions.
    - Latest news and recent events.
    - General web information not covered by scientific tools.
    
    Use the search tool to look up this information.
    """,
    tools=[mcp_duckduckgo],
)

#-----------------------------------------------------------------
# Root Agent (Orchestrator/ Manager: User facing agent)
#-----------------------------------------------------------------
root_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),#flash-lite doesn't support function calling
    name="root_agent",
    instruction=f"""
    {root_prompt}
    """,
    sub_agents=[wolfram_agent, web_search_agent, mardi_agent, calculator_agent],
)

#------------------------------------------------------------------
# Main Execution Loop
#------------------------------------------------------------------
if __name__ == "__main__":
    print("🎓 Math Tutor Agent 'Erik' Initialized!")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    # Initialize the runner with the root agent
    runner = Runner(agent=root_agent)
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye! 👋")
                break
            
            # Run the agent
            result = runner.run(user_input)
            print(f"\nErik: {result.output.text}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
