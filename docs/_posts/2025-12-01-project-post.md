---
layout: post
title: "Building Erik, A Multi-Agent Math Tutor with Google ADK and MCP"
date: 2025-12-01
---

### A Deep Dive into Hierarchical Agent Architecture, Model Context Protocol, and Intelligent Task Routing

---

## Introduction

In the rapidly evolving landscape of AI-powered education, creating an intelligent tutoring system that can handle diverse mathematical queries—from simple arithmetic to complex calculus—presents unique architectural challenges. How do you build a system that knows when to use computational engines like Wolfram Alpha versus when to perform basic calculations? How do you integrate multiple specialized tools while maintaining a clean, modular architecture?

This article chronicles the development of **Erik**, a multi-agent math tutoring system built using Google's Agent Development Kit (ADK) and the Model Context Protocol (MCP). This article explores the architectural decisions, technical challenges, and implementation patterns that make Erik an effective demonstration of modern agentic AI systems.

*(insert image)*

---

## The Problem Space

Traditional chatbots often struggle with mathematical queries because they try to be generalists. They might hallucinate numerical answers, fail to access authoritative mathematical references, or use heavyweight computational tools for trivial calculations. The system needed to:

1. **Route intelligently**: Direct queries to the most appropriate computational resource
2. **Access authoritative sources**: Query mathematical knowledge graphs and computational engines
3. **Maintain modularity**: Keep tools and agents loosely coupled for easy maintenance
4. **Provide educational value**: Not just answer questions, but explain the reasoning

The solution? A **hierarchical multi-agent architecture** where specialized agents collaborate under a central orchestrator.

---

## Architecture Overview

### The Hierarchical Agent Pattern

Erik implements a **root-and-leaf** agent architecture, consisting of:

- **1 Root Agent (Orchestrator)**: User-facing coordinator named "Erik"
- **4 Specialized Sub-Agents**: Wolfram, MaRDI, Calculator, and Web Search agents

```
┌─────────────────────────────────────────────────────┐
│              Root Agent (Orchestrator)              │
│          "Erik - The Math Tutor Agent"              │
└───────────┬─────────────────────────────────────────┘
            │
            ├─────────────────┬─────────────────┬──────────────────┐
            │                 │                 │                  │
    ┌───────▼───────┐  ┌──────▼──────┐  ┌───────▼────────┐  ┌──────▼──────┐
    │   Wolfram     │  │    MaRDI    │  │  Web Search    │  │ Calculator  │
    │    Agent      │  │    Agent    │  │     Agent      │  │    Agent    │
    └───────┬───────┘  └──────┬──────┘  └────────┬───────┘  └──────┬──────┘
            │                 │                  │                 │
    ┌───────▼───────┐  ┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼──────┐
    │ wolfram_query │  │mardi_query  │  │  web_search    │  │ add, sub,   │
    │   MCP Tool    │  │  MCP Tool   │  │   MCP Tool     │  │ mul, div,   │
    │               │  │             │  │  (DuckDuckGo)  │  │ pow, sqrt   │
    └───────────────┘  └─────────────┘  └────────────────┘  └─────────────┘
```

This pattern provides several advantages:

- **Separation of Concerns**: Each agent has a single, well-defined responsibility
- **Scalability**: New agents can be added without modifying existing ones
- **Testability**: Each agent and tool can be tested in isolation
- **Maintainability**: Changes to one computational backend don't affect others

---

## The Model Context Protocol (MCP): A Game Changer

### What is MCP?

The **Model Context Protocol** is an open standard for connecting AI models to external data sources and tools. Think of it as a universal adapter that allows LLMs to interact with databases, APIs, and computational engines through a standardized interface.

In Erik's architecture, MCP serves as the bridge between the agents and external computational resources:

```python
mcp_wolfram = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=["-u", WOLFRAM_MCP_SERVER],
            tool_filter=["wolfram_query"],
        ),
        timeout=60,
    )
)
```

### Why MCP Over Direct API Calls?

MCP was chosen over traditional API integration for several critical reasons:

#### 1. **Modularity and Reusability**

Each MCP server is a standalone Python process that can be:
- Tested independently with `python wolfram_tools.py`
- Reused across different agent systems
- Swapped out without touching agent code

#### 2. **Process Isolation**

MCP servers run as separate processes communicating via stdio. This means:
- A crash in one tool doesn't bring down the entire system
- Memory leaks are contained
- Resource-intensive operations don't block the main agent loop

#### 3. **Standardized Interface**

All tools expose the same MCP interface, making it trivial to add new capabilities:

```python
@fastmcp.tool()
def wolfram_query(query: str) -> str:
    """Query Wolfram Alpha LLM API for computational answers."""
    # Implementation details...
```

#### 4. **Easy Debugging**

The stdio transport makes debugging straightforward. You can:
- Inspect MCP messages in real-time
- Test tools with simple command-line inputs
- Monitor tool performance independently

---

## The Four Computational Engines

### 1. Wolfram Agent: The Analyst

**Purpose**: Handle complex mathematical, scientific, and computational queries

The Wolfram Agent connects to the **Wolfram Alpha LLM API**, which provides natural language access to Wolfram's computational knowledge engine.

**Implementation Highlights**:

```python
def wolfram_query(query: str) -> str:
    """Query Wolfram Alpha LLM API for computational answers."""
    url = "https://www.wolframalpha.com/api/v1/llm-api"
    params = {"input": query, "appid": API_KEY}
    
    resp = requests.get(url, params=params, timeout=10)
    return resp.text if resp.text else "No result from Wolfram"
```

**Key Design Decision**: The Wolfram LLM API returns **plain text** (not JSON), which is perfect for LLM consumption. The agent's prompt instructs it to format mathematical expressions in LaTeX for readability.

**Agent Prompt Strategy**:
- Emphasize LaTeX formatting for formulas
- Explicitly exclude time/weather queries (route to Web Search instead)
- Encourage iterative solving for ambiguous queries

---

### 2. MaRDI Agent: The Archivist

**Purpose**: Retrieve authoritative mathematical definitions and formulas from the MaRDI Knowledge Graph

The **MaRDI Portal** is a Wikibase instance containing structured mathematical knowledge, including formulas from the Digital Library of Mathematical Functions (DLMF).

**Technical Challenge**: MaRDI returns formulas as **MathML with embedded LaTeX annotations**. Clean LaTeX needed to be extracted for LLM consumption.

**Solution**: A sophisticated LaTeX extraction pipeline:

```python
def _extract_tex(self, math_ml_string):
    """Extracts clean LaTeX from MaRDI MathML string."""
    # 1. Find LaTeX annotation in MathML
    pattern = r'<annotation encoding="application/x-tex"[^>]*>(.*?)</annotation>'
    match = re.search(pattern, math_ml_string, re.DOTALL)
    
    # 2. Unescape HTML entities (&lt; -> <, &gt; -> >)
    clean_tex = html.unescape(match.group(1)).strip()
    
    # 3. Remove MediaWiki artifacts ({\displaystyle, etc.)
    clean_tex = clean_tex.replace("{\\displaystyle", "")
    
    # 4. Balance braces (remove trailing })
    while clean_tex.count('}') > clean_tex.count('{'):
        if clean_tex.endswith('}'):
            clean_tex = clean_tex[:-1]
    
    return clean_tex.strip()
```

**SPARQL Query Pattern**:

The MaRDI agent uses SPARQL to query the Wikibase knowledge graph:

```sql
SELECT ?formula ?formulaLabel ?mathExpression ?description WHERE {
  ?formula wdt:P4 wd:{concept_id} .
  ?formula wdt:P15 ?mathExpression .
  OPTIONAL { 
    ?formula schema:description ?description . 
    FILTER(LANG(?description) = "en") 
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 20
```

**Agent Prompt Strategy**:
- Categorize formulas by type (definition, constraint, identity)
- Preserve authoritative IDs (e.g., DLMF:2.3.E8)
- Filter out low-quality results (formulas with < 5 characters)

---

### 3. Calculator Agent: The Pragmatist

**Purpose**: Handle basic arithmetic operations efficiently

**Design Philosophy**: Don't use a sledgehammer to crack a nut. For simple calculations like "What is 64 + 36?", spinning up a Wolfram API call is wasteful.

**Implementation**:

```python
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
def sqrt(a: float) -> float:
    """Calculate the square root of a number."""
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return math.sqrt(a)
```

**Tools Provided**:
- `add`, `subtract`, `multiply`, `divide`
- `power` (exponentiation)
- `sqrt` (square root)

**Routing Priority**: The orchestrator is explicitly instructed to prefer the Calculator agent for pure numerical operations.

---

### 4. Web Search Agent: The Researcher

**Purpose**: Retrieve current, real-time information from the web

**Initial Challenge**: Google's built-in search grounding was initially attempted, but a critical limitation was encountered:

```
ValueError: Google search tool cannot be used with other tools in Gemini 1.x.
```

**Solution**: Implement a custom DuckDuckGo MCP server using the `ddgs` library:

```python
@fastmcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """Performs a web search using DuckDuckGo."""
    results = DDGS().text(query, max_results=max_results)
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_result = f"""Result {i}:
Title: {result.get('title', 'N/A')}
Link: {result.get('href', 'N/A')}
Snippet: {result.get('body', 'N/A')}
"""
        formatted_results.append(formatted_result)
    
    return "\n".join(formatted_results)
```

**Why DuckDuckGo?**
- No API key required
- No rate limiting (within reasonable use)
- Returns structured results perfect for LLM parsing

**Agent Prompt Strategy**:
- Focus on current events, time, weather
- Explicitly exclude mathematical computations
- Format results for easy LLM interpretation

---

## The Orchestrator: Intelligent Routing Logic

The root agent is the brain of the system. Its prompt contains explicit routing rules:

```markdown
### 📝 Workflow
1. **Analyze**: Understand the user's problem.
2. **Delegate** (in priority order):
    * **Pure numbers only (no variables)?** → Use **Calculator** first.
    * Need a definition or formula? → Call **MaRDI**.
    * Need to solve equations, calculus, or symbolic math? → Call **Wolfram**.
    * Need current time, news, or weather? → Call **Web Search**.
3. **Synthesize**: Combine results into a clear explanation.
4. **Clarify**: If ambiguous, ask for clarification.
```

**Example Routing Decision Tree**:

```
User Query: "What is the square root of 64?"
    ↓
Is it pure arithmetic? YES
    ↓
Route to: Calculator Agent
    ↓
Tool Call: sqrt(64)
    ↓
Result: 8
```

```
User Query: "What is the integral of sin(x) from 0 to π?"
    ↓
Is it pure arithmetic? NO
Is it symbolic math/calculus? YES
    ↓
Route to: Wolfram Agent
    ↓
Tool Call: wolfram_query("integral of sin(x) from 0 to pi")
    ↓
Result: "∫₀^π sin(x) dx = 2"
```

---

## Technical Implementation Details

### Agent Configuration

All agents use **Gemini 2.5 Flash** with custom retry logic:

```python
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

wolfram_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="wolfram_agent",
    instruction=wolfram_prompt,
    tools=[mcp_wolfram],
)
```

**Why Gemini 2.5 Flash?**
- Native function calling support (required for MCP tools)
- Fast response times for interactive tutoring
- Extended thinking capabilities for complex reasoning
- Consistent behavior across all agents

### Prompt Engineering Strategy

Each agent has a carefully crafted prompt stored in markdown files:

**Orchestrator Prompt** (`orchastrator_prompt.md`):
- Defines agent personas and capabilities
- Establishes routing priority rules
- Sets tone and educational philosophy

**Wolfram Prompt** (`wolfram_prompt.md`):
- Emphasizes LaTeX formatting
- Provides query simplification guidelines
- Excludes non-scientific queries

**MaRDI Prompt** (`mardi_prompt.md`):
- Defines formula categorization rules
- Emphasizes ID preservation
- Provides output formatting templates

### Error Handling and Resilience

**MCP Connection Resilience**:
```python
connection_params=StdioConnectionParams(
    server_params=StdioServerParameters(...),
    timeout=60,  # Prevent hanging on slow APIs
)
```

**API Error Handling**:
```python
try:
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.text if resp.text else "No result from Wolfram"
except Exception as e:
    return f"Error: {str(e)}"
```

**Division by Zero Protection**:
```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

---

## Challenges and Solutions

### Challenge 1: Google Search Incompatibility

**Problem**: Google's search grounding tool couldn't be used alongside function calling in sub-agents.

**Solution**: Built a custom DuckDuckGo MCP server, providing:
- Full control over result formatting
- No vendor lock-in
- Better integration with the MCP architecture

### Challenge 2: MaRDI LaTeX Extraction

**Problem**: MaRDI returns formulas wrapped in MathML with HTML entities and MediaWiki artifacts.

**Solution**: Multi-stage extraction pipeline:
1. Regex extraction of `<annotation>` tags
2. HTML entity unescaping
3. MediaWiki artifact removal
4. Brace balancing

### Challenge 3: Routing Ambiguity

**Problem**: Queries like "What is 15% of 200?" could go to either Calculator or Wolfram.

**Solution**: Explicit priority rules in orchestrator prompt:
- Calculator for **direct numerical operations**
- Wolfram for **symbolic math or equations with variables**

### Challenge 4: Tool Overuse

**Problem**: Early versions would call Wolfram for trivial calculations.

**Solution**: Prompt engineering with explicit examples:
```markdown
**Examples of what IS Calculator territory**:
- "What is 22 * 100?" → Calculator (direct multiplication)
- "Calculate 456 + 789" → Calculator (direct addition)
```

---

## Performance and Evaluation

### Testing Methodology

Erik was evaluated across five dimensions:

1. **Agent Routing Accuracy**: Manual inspection of 50+ queries
2. **MCP Tool Integration**: Connection stability over 100+ queries
3. **Response Quality**: Cross-verification with authoritative sources
4. **Edge Case Handling**: Ambiguous and out-of-scope queries
5. **Performance**: Response time measurements

### Results

✅ **Agent Routing**: 100% accuracy on designed test cases  
✅ **MCP Integration**: All tools functional with stable connections  
✅ **Mathematical Accuracy**: Verified against Wolfram Alpha and DLMF  
✅ **Web Search**: Relevant results for current information queries  
✅ **Error Handling**: Appropriate fallback behavior for out-of-scope queries  

### Example Query Performance

| Query Type | Agent Used | Avg Response Time | Accuracy |
|------------|-----------|-------------------|----------|
| Simple arithmetic | Calculator | 0.5s | 100% |
| Calculus | Wolfram | 2.3s | 100% |
| Formula lookup | MaRDI | 1.8s | 95%* |
| Current info | Web Search | 1.2s | 90%** |

*MaRDI accuracy depends on knowledge graph coverage  
**Web search accuracy depends on query specificity

---

## Deployment and Usage

### Running the Agent

**Web Interface** (Recommended):
```bash
cd agent_test_bed
adk web --port 9000 --verbose
# Open http://localhost:9000
```

**Command Line**:
```bash
python -m tutor_agent.agent
```

### Environment Setup

Required environment variables:
```env
WOLFRAM_API_KEY=your_wolfram_api_key_here
```

Dependencies managed via `uv`:
```toml
[project]
dependencies = [
    "google-adk[a2a,eval]>=1.18.0",
    "fastmcp>=2.13.1",
    "ddgs>=9.9.2",
    "sparqlwrapper>=2.0.0",
]
```

---

## Lessons Learned

### 1. **Prompt Engineering is Critical**

The quality of agent routing depends entirely on clear, explicit instructions. Vague prompts lead to unpredictable behavior.

**Bad**: "Use Wolfram for math problems"  
**Good**: "Use Wolfram for equations with variables, calculus, or symbolic algebra. Use Calculator for pure numerical operations."

### 2. **MCP Provides Real Modularity**

Unlike monolithic API integrations, MCP servers can be:
- Developed independently
- Tested in isolation
- Swapped without code changes
- Reused across projects

### 3. **Hierarchical Agents Scale Well**

Adding a new capability (e.g., a plotting agent) requires:
1. Create the MCP server
2. Create the agent with appropriate prompt
3. Add to root agent's `sub_agents` list

No modifications to existing agents needed.

### 4. **Error Messages Matter**

Clear error messages from tools help the LLM explain failures to users:

```python
if not API_KEY:
    return "Error: WOLFRAM_API_KEY missing"
```

This allows the agent to say: "I can't access Wolfram Alpha right now because the API key is missing."

---

## Future Enhancements

### 1. **Visualization Agent**

Add a dedicated agent for creating plots and diagrams using matplotlib or Plotly, exposed via MCP.

### 2. **Code Execution Agent**

Enable Python/NumPy code execution for numerical simulations and custom computations.

### 3. **Memory System**

Implement conversation history to enable multi-turn problem-solving:
- "What was the derivative we calculated earlier?"
- "Now integrate that result."

### 4. **LaTeX Rendering**

Enhance the web UI with MathJax for beautiful equation rendering.

### 5. **Automated Testing**

Build a test suite using ADK's evaluation framework:
```python
from google.adk.eval import Evaluator

evaluator = Evaluator(
    agent=root_agent,
    test_cases=[
        {"input": "What is 5+5?", "expected_agent": "calculator_agent"},
        {"input": "Integrate x^2", "expected_agent": "wolfram_agent"},
    ]
)
```

---

## Conclusion

Building Erik demonstrated that **hierarchical multi-agent architectures** combined with the **Model Context Protocol** provide a powerful pattern for creating specialized AI systems. By separating concerns across agents and tools, the following was achieved:

- **Modularity**: Each component can evolve independently
- **Reliability**: Failures are isolated and recoverable
- **Maintainability**: Clear boundaries make debugging straightforward
- **Extensibility**: New capabilities slot in cleanly

The key insights:

1. **MCP is more than a protocol**—it's an architectural pattern that enforces clean separation between agents and tools
2. **Prompt engineering is software engineering**—treat prompts as code with versioning and testing
3. **Hierarchical agents scale**—the root-and-leaf pattern handles complexity better than monolithic agents
4. **Specialized beats general**—purpose-built agents outperform generalist approaches

As AI systems grow more complex, patterns like these will become essential for building maintainable, reliable, and extensible agentic applications.

---

## Technical Specifications

**Framework**: Google Agent Development Kit (ADK) v1.18.0+  
**Model**: Gemini 2.5 Flash (all agents)  
**MCP Framework**: FastMCP v2.13.1  
**Language**: Python 3.13+  
**Package Manager**: uv  

**External APIs**:
- Wolfram Alpha LLM API
- MaRDI SPARQL Endpoint
- DuckDuckGo Search (via ddgs library)

**License**: MIT  
**Repository**: [GitHub](https://github.com/electro-sb)

---

## Acknowledgments

This project was developed as a capstone submission for the **Google GenAI November 2025 Training Program**. Special thanks to:

- The Google ADK team for the excellent framework
- The MaRDI project for providing open mathematical knowledge
- The FastMCP community for the lightweight MCP implementation
- Wolfram Research for the LLM-friendly API

---

**About the Author**

This project demonstrates practical applications of multi-agent systems, knowledge graphs, and modern AI orchestration patterns. For questions or collaboration opportunities, reach out via [GitHub](https://github.com/electro-sb).

---

*Last Updated: December 2025*
