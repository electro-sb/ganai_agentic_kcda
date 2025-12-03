---
layout: post
title: "Extending Erik with Agent-to-Agent Communication: Building a Distributed Math Tutoring System"
date: 2025-12-03
---

### From Monolithic Agent to Distributed Service: Implementing the A2A Protocol

---

## Introduction

After building **Erik**, a multi-agent math tutor with hierarchical architecture and MCP tool integration, the next natural question emerged: *How can other AI agents leverage Erik's specialized capabilities?* 

This article explores the implementation of **Agent-to-Agent (A2A) communication** to transform Erik from a standalone application into a **distributed service** that can be consumed by remote agents. We'll dive into the A2A protocol, prompt engineering for client agents, and the architectural patterns that make distributed agentic systems possible.

---

## The Problem: Agent Reusability

Erik is powerful—it orchestrates four specialized sub-agents (Wolfram, MaRDI, Calculator, Web Search) to solve mathematical problems. But what if you're building a different agent (say, a homework helper or a research assistant) that occasionally needs math expertise?

**Traditional Approach**: Copy Erik's code, duplicate the MCP servers, manage separate instances.

**A2A Approach**: Expose Erik as a **remote service** that other agents can call via a standardized protocol.

### Benefits of A2A

1. **Separation of Concerns**: Client agents focus on their domain, delegate math to Erik
2. **Resource Efficiency**: One Erik instance serves multiple clients
3. **Maintainability**: Updates to Erik benefit all clients automatically
4. **Modularity**: Swap out Erik for a different math service without changing client code

---

## Architecture Overview

The A2A implementation consists of two components:

```
┌─────────────────────────────────────────────────────────┐
│                    User                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Math Student Client (a2a_client)                │
│         - Receives user questions                       │
│         - Delegates to Eric via A2A                     │
│         - Relays responses                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP (A2A Protocol)
                     │ http://localhost:8001
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Erik Tutor Server (a2a_tutor_serv)              │
│         - Exposes agent card                            │
│         - Handles A2A requests                          │
│         - Returns responses                             │
│                                                         │
│         ┌─────────────────────────────────────┐         │
│         │  Erik (Root Agent)                  │         │
│         │  ├─ Wolfram Agent                   │         │
│         │  ├─ MaRDI Agent                     │         │
│         │  ├─ Calculator Agent                │         │
│         │  └─ Web Search Agent                │         │
│         └─────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

## The A2A Protocol

### What is A2A?

The **Agent-to-Agent (A2A) protocol** is a standardized way for AI agents to communicate. It defines:

1. **Agent Cards**: Metadata describing an agent's capabilities (JSON at `/.well-known/agent-card.json`)
2. **Message Format**: Structured request/response payloads
3. **Discovery**: How clients find and connect to remote agents

### Agent Card Example

When Erik is exposed via A2A, it publishes an agent card:

```json
{
  "name": "root_agent",
  "description": "Erik - A friendly Math Tutor Agent",
  "url": "http://localhost:8001",
  "skills": [
    {
      "name": "math_tutoring",
      "description": "Solve math problems using Wolfram, MaRDI, Calculator, and Web Search"
    }
  ]
}
```

Clients fetch this card to understand Erik's capabilities before making requests.

---

## Implementation: Server Side

### Converting Erik to an A2A Service

Using Google ADK's `to_a2a` utility, Erik becomes an A2A server with a single line:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Erik's existing agent definition
root_tutor_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash"),
    name="root_agent",
    instruction=root_prompt,
    sub_agents=[wolfram_agent, web_search_agent, mardi_agent, calculator_agent],
)

# Expose as A2A service
app = to_a2a(root_tutor_agent, port=8001)
```

### Server Launch Script

To manage the server lifecycle, a dedicated launch script was created:

```python
# a2a_server_launch.py
server_process = subprocess.Popen(
    [
        "uvicorn",
        "agent:app",
        "--host", "localhost",
        "--port", "8001",
    ],
    cwd=A2A_SERVER_PATH,
    preexec_fn=os.setsid  # Process group for clean shutdown
)

# Wait for server to be ready
for attempt in range(MAX_ATTEMPTS):
    try:
        response = requests.get(AGENT_CARD_URL, timeout=1)
        if response.status_code == 200:
            print("✅ Eric Tutor A2A server is running!")
            break
    except requests.exceptions.RequestException:
        time.sleep(POLL_INTERVAL_SECONDS)

# Keep running until Ctrl+C
try:
    server_process.wait()
except KeyboardInterrupt:
    os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
```

**Key Features**:
- Polls for server readiness (checks agent card endpoint)
- Graceful shutdown with SIGTERM
- Process group management to kill Uvicorn workers

---

## Implementation: Client Side

### The Math Student Client

The client agent acts as an **intelligent intermediary** between users and Erik:

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

# Connect to Erik server
eric_tutor = RemoteA2aAgent(
    name="eric_tutor",
    description="Remote Eric tutor agent that provides math tutoring services.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Client agent that uses Erik
root_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash"),
    name="math_student_client",
    instruction=client_prompt,
    sub_agents=[eric_tutor],
)
```

### The Critical Part: Client Prompt Engineering

The client's prompt is **the key to successful delegation**. Here's the design:

```markdown
You are a **Math Student Client Agent** that helps users get answers 
to their math questions by consulting **Eric**, a specialized math tutor.

### 🎯 Your Role
1. **Understand** the user's math-related questions
2. **Delegate** appropriate questions to Eric (the `eric_tutor` sub-agent)
3. **Present** Eric's responses clearly to the user
4. **Handle** non-math questions directly if they're simple general queries

### 🤖 Your Team
- **Eric Tutor** (`eric_tutor`): A comprehensive math tutor agent with access to:
  - Wolfram Alpha (complex math, equations, calculus, physics, chemistry)
  - MaRDI Knowledge Graph (mathematical definitions and formulas)
  - Calculator (basic arithmetic operations)
  - Web Search (current time, weather, news, general information)

### 📝 When to Use Eric
**ALWAYS delegate to Eric for**:
- Any mathematical calculations (simple or complex)
- Math problem solving (algebra, calculus, geometry, etc.)
- Mathematical definitions and formulas
- Physics or chemistry problems
- Scientific constants or conversions
- Questions requiring current information (time, weather, news)

**Examples**:
- "What is 22 * 100?" → Delegate to Eric
- "Solve x^2 + 5x + 6 = 0" → Delegate to Eric
- "What is the definition of the Gamma function?" → Delegate to Eric

**Handle directly only for**:
- Simple greetings ("Hello", "Hi")
- Meta questions about your capabilities ("What can you do?")

### 🔄 Workflow
1. **Receive** user's question
2. **Analyze** if it requires Eric's expertise
3. **Delegate** to Eric by calling the `eric_tutor` sub-agent
4. **Relay** Eric's response to the user clearly
5. **Follow up** if the user has additional questions

### ⛔ Constraints
- **Never guess** at math answers - always use Eric
- **Never perform calculations yourself** - delegate to Eric
- **Be friendly** and supportive in your communication
- **Trust Eric's expertise** - he has the right tools for the job
```

---

## Prompt Engineering Principles

### 1. Clear Role Definition

**Why it matters**: The client must understand it's a **delegator**, not a **solver**.

**Bad**: "You are a math tutor."  
**Good**: "You are a client that consults Eric, a specialized math tutor."

### 2. Explicit Delegation Rules

**Why it matters**: Prevents the client from trying to solve problems itself.

**Implementation**:
- ✅ **ALWAYS delegate**: Math, science, current info
- ❌ **Handle directly**: Greetings, meta questions

### 3. Concrete Examples

**Why it matters**: LLMs learn better from examples than descriptions.

**Pattern**:
```markdown
- "What is 22 * 100?" → Delegate to Eric
- "Solve x^2 + 5x + 6 = 0" → Delegate to Eric
```

### 4. Structured Workflow

**Why it matters**: Ensures consistent behavior across queries.

**5-Step Process**:
1. Receive → 2. Analyze → 3. Delegate → 4. Relay → 5. Follow up

### 5. Hard Constraints

**Why it matters**: Prevents edge case failures.

**Examples**:
- "Never guess at math answers"
- "Never perform calculations yourself"

---

## Technical Challenges and Solutions

### Challenge 1: Import Path Issues

**Problem**: Initial implementation used non-existent `from_a2a` utility:

```python
from google.adk.a2a.utils.a2a_to_agent import from_a2a  # ❌ Doesn't exist
```

**Solution**: Use the correct `RemoteA2aAgent` class:

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent  # ✅ Correct
```

### Challenge 2: Runner Configuration

**Problem**: Gradio app failed with:
```
ValueError: Either app or both app_name and agent must be provided.
```

**Solution**: Provide both `app_name` and `agent` to Runner:

```python
runner = Runner(
    app_name="math_student_client",  # Required
    agent=root_agent,
    session_service=session_service,
)
```

### Challenge 3: Server Lifecycle Management

**Problem**: Orphaned Uvicorn processes after script termination.

**Solution**: Process group management with cleanup script:

```bash
#!/bin/bash
# sweep_orphans_opt.sh
PID=$(lsof -t -i tcp:"$SERVER_PORT")
if [ -n "$PID" ]; then
    kill "$PID"
    sleep 2
    if ps -p "$PID" > /dev/null; then
        kill -9 "$PID"
    fi
fi
```

---

## Usage Patterns

### Pattern 1: ADK Web UI (Recommended)

**Terminal 1** - Start Erik server:
```bash
cd a2a_flow
python a2a_server_launch.py
```

**Terminal 2** - Start client:
```bash
cd a2a_flow/a2a_client
adk web --port 9000
```

Open http://localhost:9000 for the chat interface.

### Pattern 2: Programmatic Access

```python
from agent import root_agent
from google.adk.runners import Runner

runner = Runner(
    app_name="math_client",
    agent=root_agent,
    session_service=InMemorySessionService(),
)

response = runner.run(
    session_id="session_123",
    user_message="What is the integral of sin(x) from 0 to pi?"
)

print(response.content)
```

---

## Comparison: Monolithic vs. A2A Architecture

| Aspect | Monolithic Erik | A2A Erik |
|--------|----------------|----------|
| **Deployment** | Single process | Server + Client(s) |
| **Reusability** | Code duplication | Service reuse |
| **Scaling** | Vertical only | Horizontal possible |
| **Updates** | Requires redeployment | Server update benefits all clients |
| **Network** | Local only | Can be remote |
| **Complexity** | Lower | Higher (networking, lifecycle) |

**When to use A2A**:
- Multiple agents need math capabilities
- Centralized expertise management
- Resource pooling (one Wolfram API key serves all)

**When to use Monolithic**:
- Single-purpose application
- Low latency requirements
- Simpler deployment

---

## Lessons Learned

### 1. Prompt Engineering is Critical for Delegation

The client's prompt must be **crystal clear** about when to delegate. Vague instructions lead to:
- Client attempting to solve math itself
- Unnecessary delegation of simple queries
- Inconsistent behavior

### 2. A2A Adds Operational Complexity

Benefits of distributed architecture come with costs:
- Server lifecycle management
- Network reliability concerns
- Debugging across process boundaries

### 3. Agent Cards Enable Discovery

The `/.well-known/agent-card.json` endpoint is crucial for:
- Client validation (is the server running?)
- Capability discovery (what can Erik do?)
- Version compatibility checks

### 4. Process Management Matters

Proper shutdown handling prevents:
- Orphaned Uvicorn workers
- Port conflicts on restart
- Resource leaks

---

## Future Enhancements

### 1. Authentication and Authorization

Add API key validation for production deployments:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

### 2. Load Balancing

Deploy multiple Erik instances behind a load balancer:

```
Client → Load Balancer → Erik Instance 1
                      → Erik Instance 2
                      → Erik Instance 3
```

### 3. Caching Layer

Cache frequent queries to reduce Wolfram API calls:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_wolfram_query(query: str) -> str:
    return wolfram_query(query)
```

### 4. Monitoring and Observability

Add structured logging and metrics:

```python
import structlog

logger = structlog.get_logger()
logger.info("a2a_request", client="math_student", query=user_message)
```

### 5. Multi-Agent Orchestration

Build a **meta-orchestrator** that routes to multiple specialized agents:

```
User → Meta Client → Erik (Math)
                  → LegalBot (Law)
                  → MedAgent (Medicine)
```

---

## Conclusion

Extending Erik with A2A communication demonstrates how **specialized agents can become reusable services** in a distributed AI ecosystem. Key takeaways:

1. **A2A enables agent reusability** - One Erik instance serves multiple clients
2. **Prompt engineering is crucial** - Client prompts must clearly define delegation rules
3. **Operational complexity increases** - Server lifecycle, networking, and debugging require careful design
4. **Standardization matters** - Agent cards and protocols enable interoperability

As agentic systems grow more complex, patterns like A2A will become essential for building **composable, maintainable, and scalable AI architectures**.

The future of AI isn't monolithic superintelligence—it's **networks of specialized agents** collaborating through standardized protocols.

---

## Technical Specifications

**A2A Framework**: Google ADK A2A utilities  
**Server**: Uvicorn (ASGI)  
**Protocol**: HTTP/JSON  
**Client**: RemoteA2aAgent  
**Model**: Gemini 2.5 Flash  

**Repository**: [GitHub](https://github.com/electro-sb)  
**License**: MIT  

---

## Acknowledgments

This A2A implementation builds on the foundational Erik agent developed for the **Google GenAI November 2025 Training Program**. Special thanks to the Google ADK team for the excellent A2A utilities and documentation.

---

*Last Updated: December 2025*
