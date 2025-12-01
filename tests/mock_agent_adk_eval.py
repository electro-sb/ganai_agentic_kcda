# test_router_agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from dotenv import load_dotenv
import os

load_dotenv()

# --- 1. Define Fake Tools (Mocking Sub-Agents) ---
def call_wolfram(query: str):
    """Useful for solving math problems, derivatives, integrals, and scientific facts."""
    return "MATCH_WOLFRAM"  # Simple keyword for eval to catch

def call_mardi(query: str):
    """Useful for searching scientific datasets, MaRDI database, and papers."""
    return "MATCH_MARDI"

def call_calculator(query: str):
    """Useful for trivial arithmetic like addition, subtraction, multiplication."""
    return "MATCH_CALC"

def call_web_search(query: str):
    """Useful for current events, weather, news, and general web info."""
    return "MATCH_SEARCH"

# --- 2. Load Your Real Routing Prompt ---
# Ensure the path is correct relative to where you run the command
try:
    with open("./tutor_agent/prompts/orchastrator_prompt.md", "r") as f:
        root_prompt_text = f.read()
except FileNotFoundError:
    root_prompt_text = "You are a helpful assistant. Route queries to the correct tool."

# --- 3. Export the 'agent' variable ---
# 'adk eval' will import this variable automatically
agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash"),
    name="router_eval_agent",
    instruction=f"""
    {root_prompt_text}
    
    IMPORTANT: You have access to tools that represent your agents. 
    Use the correct tool for the user's query.
    """,
    tools=[call_wolfram, call_mardi, call_calculator, call_web_search]
)
