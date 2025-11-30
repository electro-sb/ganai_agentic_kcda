[![Profile](./assets/badges/profile.svg)](https://github.com/electro-sb)
###### Project Information:
<!--- Badges --->
[![Project](./assets/badges/Project.svg)](./README.md)
[![Version](./assets/badges/version.svg)](./pyproject.toml)
###### Metadata:
<!--- Badges --->
[![Git Commit](./assets/badges/git.svg)](./README.md)
[![Last Updated](./assets/badges/updated.svg)](./README.md)


# Erik - Math Tutor Agent 🎓

## Overview

**Erik** is an intelligent, multi-agent AI system designed to help users solve mathematical problems through a coordinated team of specialized agents. Built using Google's Agent Development Kit (ADK) and the Model Context Protocol (MCP), Erik demonstrates advanced agentic architecture with clear separation of concerns and intelligent task routing.

The system leverages multiple computational engines (Wolfram Alpha, MaRDI Knowledge Graph, DuckDuckGo Search) and combines them through a sophisticated orchestration layer to provide accurate, step-by-step mathematical assistance.

---

## Architecture

Erik follows a **hierarchical multi-agent architecture** with a root orchestrator coordinating specialized sub-agents:

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
    │  (Analyst)    │  │ (Archivist) │  │  (Researcher)  │  │  (Basic     │
    │               │  │             │  │                │  │   Math)     │
    └───────┬───────┘  └──────┬──────┘  └────────┬───────┘  └──────┬──────┘
            │                 │                  │                 │
    ┌───────▼───────┐  ┌──────▼──────┐  ┌────────▼───────┐  ┌──────▼──────┐
    │ wolfram_query │  │mardi_query  │  │  web_search    │  │ add, sub,   │
    │   MCP Tool    │  │  MCP Tool   │  │   MCP Tool     │  │ mul, div,   │
    │               │  │             │  │  (DuckDuckGo)  │  │ pow, sqrt   │
    └───────────────┘  └─────────────┘  └────────────────┘  └─────────────┘
```

---

## Agent Descriptions

### 1. **Root Agent (Orchestrator)** - "Erik"
- **Model**: `gemini-2.5-flash`
- **Role**: User-facing coordinator that analyzes requests and delegates to appropriate sub-agents
- **Responsibilities**:
  - Understand user's mathematical problem
  - Break down complex queries into sub-tasks
  - Route requests to the correct specialist agent
  - Synthesize responses from multiple agents
  - Provide clear, educational explanations
- **Tools**: Access to all 4 sub-agents via transfer mechanism

### 2. **Wolfram Agent** - "The Analyst"
- **Model**: `gemini-2.5-flash`
- **Role**: Handles complex mathematical, scientific, and computational queries
- **Responsibilities**:
  - Solve integrals, derivatives, equations
  - Perform symbolic mathematics
  - Provide scientific data and constants
  - Generate plots and visualizations
- **Tools**: `wolfram_query` (MCP connection to Wolfram Alpha LLM API)
- **Prompt Focus**: Scientific precision, LaTeX formatting, no time/weather queries

### 3. **MaRDI Agent** - "The Archivist"
- **Model**: `gemini-2.5-flash`
- **Role**: Retrieves mathematical definitions, formulas, and identities from the MaRDI Knowledge Graph
- **Responsibilities**:
  - Look up formal mathematical definitions
  - Find mathematical identities and theorems
  - Extract domain constraints and validity conditions
  - Provide authoritative references (e.g., DLMF IDs)
- **Tools**: `mardi_query` (MCP connection to MaRDI SPARQL endpoint)
- **Prompt Focus**: Structured extraction, preserving IDs, categorizing constraints

### 4. **Calculator Agent** - "The Calculator"
- **Model**: `gemini-2.5-flash`
- **Role**: Handles basic arithmetic operations
- **Responsibilities**:
  - Simple calculations: addition, subtraction, multiplication, division
  - Power and square root operations
  - Quick numerical computations
- **Tools**: `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt` (MCP tools)
- **Prompt Focus**: Direct, no-frills computation

### 5. **Web Search Agent** - "The Researcher"
- **Model**: `gemini-2.5-flash`
- **Role**: Retrieves current, real-time information from the web
- **Responsibilities**:
  - Current time/date queries
  - Weather information
  - Recent news and events
  - General web information not covered by scientific tools
- **Tools**: `web_search` (MCP connection to DuckDuckGo)
- **Prompt Focus**: Real-time data, current events, general knowledge

---

## MCP Tool Servers

The system uses the **Model Context Protocol (MCP)** to connect to external computational resources via stdio-based MCP servers:

### 1. **Wolfram Tools** (`wolfram_tools.py`)
- **API**: Wolfram Alpha LLM API
- **Authentication**: Requires `WOLFRAM_API_KEY` environment variable
- **Tool**: `wolfram_query(query: str) -> str`
- **Returns**: Plain text computational answers

### 2. **MaRDI Tools** (`mardi_tools.py`)
- **API**: MaRDI Knowledge Graph SPARQL endpoint
- **Authentication**: Public endpoint (no key required)
- **Tool**: `mardi_query(query: str) -> str`
- **Returns**: JSON array of mathematical formulas with IDs and metadata

### 3. **DuckDuckGo Tools** (`duckduckgo_tools.py`)
- **API**: DuckDuckGo Search (via `ddgs` Python library)
- **Authentication**: None required
- **Tool**: `web_search(query: str, max_results: int) -> str`
- **Returns**: Formatted search results (title, link, snippet)

### 4. **Calculator Tools** (`calculator.py`)
- **Implementation**: Pure Python arithmetic operations
- **Tools**: `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt`
- **Returns**: Numerical results

---

## Workflow: How a Query is Processed

1. **User Input**: User asks a question (e.g., "What is the derivative of x²?")

2. **Root Agent Analysis**:
   - Parses the user's intent
   - Categorizes the question type (definition? calculation? current info?)
   - Consults orchestrator prompt for routing rules

3. **Agent Selection**:
   - **Math problem** → Wolfram Agent
   - **Definition lookup** → MaRDI Agent
   - **Simple arithmetic** → Calculator Agent
   - **Current time/news/weather** → Web Search Agent

4. **Sub-Agent Execution**:
   - Selected agent receives the query
   - Agent formulates appropriate tool call
   - MCP server processes request and returns result
   - Agent interprets and formats the response

5. **Response Synthesis**:
   - Root agent receives sub-agent's output
   - Combines information if multiple agents were consulted
   - Formats final answer with educational context
   - Returns to user

---

## Technical Stack

### Core Framework
- **Google ADK** (Agent Development Kit) `v1.18.0+`
  - `LlmAgent`: Agent abstraction
  - `Runner`: Execution engine
  - `McpToolset`: MCP integration

### Models
- **Gemini 2.5 Flash**: Primary model for all agents
  - Supports function calling
  - Native MCP tool integration
  - Extended thinking capabilities

### MCP Infrastructure
- **FastMCP**: Lightweight MCP server framework
- **stdio transport**: Process-based MCP connections
- **Tool filtering**: Selective tool exposure per agent

### External APIs
- **Wolfram Alpha LLM API**: Computational intelligence
- **MaRDI SPARQL API**: Mathematical knowledge graph
- **DuckDuckGo Search**: Web search (via `ddgs` library)

### Environment
- **Python**: 3.13+
- **Package Manager**: `uv`
- **Configuration**: `.env` for API keys

---

## Setup Instructions

### Prerequisites
```bash
# Python 3.13+
python --version

# UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation
```bash
# Clone repository
cd agent_test_bed/tutor_agent

# Set up environment variables
cp .env.example .env
# Edit .env and add your WOLFRAM_API_KEY

# Install dependencies (handled by uv in parent project)
cd ../..
uv sync
```

### Configuration

Create `.env` file in `agent_test_bed/` with:
```env
WOLFRAM_API_KEY=your_wolfram_api_key_here
```

### Running the Agent

#### Web Interface (Recommended)
```bash
cd agent_test_bed
adk web --port 9000 --verbose
# Open http://localhost:9000 in a browser
```

#### Command Line Interface
```bash
cd agent_test_bed
python -m tutor_agent.agent
```

---

## Project Structure (important files)

```shell
# Core agent files
./tutor_agent/
├── __init__.py
├── .env
├── agent.py
└── prompts
    ├── mardi_prompt.md
    ├── orchastrator_prompt.md
    └── wolfram_prompt.md

# MCP tool files
./mcp_tool_chest/
├── wolfram_tools.py
├── mardi_tools.py
├── duckduckgo_tools.py
└── calculator.py

# Documentation files
./
├── README.md
├── LICENSE.md
```

---

## Key Design Decisions

### 1. **Gemini 2.5 Flash for All Agents**
- Initially tried Gemini 2.0 Flash Exp for web search agent
- Issue: Google Search tool had compatibility issues with function calling
- Solution: Switched to DuckDuckGo + Gemini 2.5 Flash for consistency

### 2. **Explicit Agent Instructions**
- Each agent has tailored instructions in markdown files
- Orchestrator prompt explicitly defines when to use each agent
- Prevents incorrect routing (e.g., Wolfram for time queries)

### 3. **MCP Over Direct API Calls**
- Modularity: Tools can be swapped independently
- Reusability: MCP servers can be used by other agents
- Debugging: stdio protocol makes it easy to test tools in isolation

### 4. **Formatted Tool Outputs**
- DuckDuckGo: Readable text format (not JSON) for better LLM parsing
- MaRDI: Preserves formula IDs for reference attribution
- Wolfram: Plain text (Wolfram API returns human-readable responses)

---

## Example Usage

### Example 1: Complex Math
**User**: "What is the integral of sin(x) from 0 to π?"

**Flow**:
1. Root Agent → Wolfram Agent
2. Wolfram Agent → `wolfram_query("integral of sin(x) from 0 to pi")`
3. Response: "∫₀^π sin(x) dx = 2"

### Example 2: Mathematical Definition
**User**: "What is the definition of the Gamma function?"

**Flow**:
1. Root Agent → MaRDI Agent
2. MaRDI Agent → `mardi_query("Gamma function")`
3. Response: 
   - **[DLMF:2.3.E8]**: Γ(z) = ∫₀^∞ t^(z-1) e^(-t) dt
   - **[DLMF:2.3.E9]**: Re(z) > 0 - *Validity Constraint*

### Example 3: Current Information
**User**: "What is the current Pacific time in USA?"

**Flow**:
1. Root Agent → Web Search Agent
2. Web Search Agent → `web_search("current pacific time")`
3. Response: Links to time.is/PST with current PST/PDT time

### Example 4: Simple Arithmetic
**User**: "What is 25 * 4?"

**Flow**:
1. Root Agent → Calculator Agent
2. Calculator Agent → `multiply(25, 4)`
3. Response: "100"

---

## Future Improvements

### Potential Enhancements
1. **Memory/Session Management**: Remember previous queries in conversation
2. **Visualization Agent**: Dedicated agent for creating plots/diagrams
3. **Code Execution Agent**: Run Python/NumPy for numerical simulations
4. **LaTeX Rendering**: Better mathematical notation in responses
5. **Multi-step Problem Solving**: Guided problem-solving workflows
6. **Knowledge Caching**: Cache MaRDI/Wolfram responses for faster retrieval
7. **Web UI Enhancement**: Custom frontend with equation editor

### Known Limitations
- DuckDuckGo search may have rate limiting
- Wolfram API has quota limits (free tier: 2000 queries/month)
- MaRDI coverage is limited to certain mathematical domains
- No persistent conversation history

---

## Troubleshooting

### Common Issues

**Issue**: `ValueError: Google search tool cannot be used with other tools in Gemini 1.x.`
- **Cause**: Google Search grounding incompatible with function calling in older models
- **Solution**: Use DuckDuckGo MCP tool instead (already implemented)

**Issue**: Empty results from DuckDuckGo
- **Cause**: Old `duckduckgo_search` package deprecated
- **Solution**: Use `ddgs` package (v9.9.2+)

**Issue**: Wolfram agent being used for time queries
- **Cause**: Orchestrator prompt not specific enough
- **Solution**: Updated orchestrator prompt to explicitly exclude time/weather from Wolfram

**Issue**: MCP session cleanup warnings
- **Cause**: Known issue with anyio cancel scopes in MCP library
- **Solution**: Safe to ignore; doesn't affect functionality

---

<!--- Badges --->
[![License](./assets/badges/license.svg)](./LICENSE.md)

---

## Credits

- **Framework**: Google Agent Development Kit (ADK)
- **APIs**: Wolfram Alpha, MaRDI Knowledge Graph, DuckDuckGo
- **Development**: Capstone Project submission (Google GenAI November 2025 Training)

---
## Contact
[![Profile](./assets/badges/github.svg)](https://github.com/electro-sb)

