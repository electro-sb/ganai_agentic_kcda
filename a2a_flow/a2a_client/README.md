# A2A Client Agent - Math Student Client

This agent acts as a client that connects to the **Eric** math tutor server (a2a_tutor_serv) using the Agent-to-Agent (A2A) protocol.

## 🎯 Purpose

The `math_student_client` agent serves as an intelligent intermediary between users and the Eric tutor server. It:
- Receives math questions from users
- Delegates them to Eric (the remote tutor agent)
- Returns Eric's responses to the user

## 🏗️ Architecture

```
User → math_student_client (a2a_client) → Eric Tutor (a2a_tutor_serv)
                                              ↓
                                         Sub-agents:
                                         - Wolfram Agent
                                         - MaRDI Agent
                                         - Calculator Agent
                                         - Web Search Agent
```

## 📝 Prompt Design

The client agent's prompt is designed with the following key sections:

### 1. **Role Definition**
The agent understands it's a client interface to Eric, not a standalone math solver.

### 2. **Team Description**
Clear explanation of Eric's capabilities and the tools he has access to.

### 3. **Delegation Rules**
Explicit instructions on when to delegate to Eric:
- ✅ **Always delegate**: Math calculations, problem solving, definitions, current info
- ❌ **Handle directly**: Simple greetings, meta questions

### 4. **Workflow**
Step-by-step process for handling user requests:
1. Receive question
2. Analyze if Eric is needed
3. Delegate to Eric
4. Relay response
5. Follow up

### 5. **Best Practices**
- Be transparent about consulting Eric
- Be efficient - let Eric's expertise shine
- Be helpful with technical clarifications
- Be accurate - always rely on Eric

### 6. **Constraints**
- Never guess at math answers
- Never perform calculations directly
- Always delegate to Eric for math/science
- Be friendly and supportive

## 🔌 Connection Setup

The client connects to Eric using the `from_a2a` utility:

```python
eric_tutor = from_a2a(
    name="eric_tutor",
    url="http://localhost:8001",  # Port where a2a_tutor_serv is running
)
```

## 🚀 Usage

### Starting the Server (Eric)
First, start the Eric tutor server:
```bash
cd a2a_flow/a2a_tutor_serv
python agent.py
```

### Running the Client
Then run the client agent:
```bash
cd a2a_flow/a2a_client
# Your client code here
```

## 💡 Example Interactions

### Example 1: Simple Calculation
**User**: "What is 22 * 100?"
**Client**: Delegates to Eric → Eric uses Calculator → Returns "2200"

### Example 2: Complex Math
**User**: "Solve x^2 + 5x + 6 = 0"
**Client**: Delegates to Eric → Eric uses Wolfram → Returns solution with steps

### Example 3: Math Definition
**User**: "What is the Gamma function?"
**Client**: Delegates to Eric → Eric uses MaRDI → Returns definition

### Example 4: Current Information
**User**: "What time is it in Tokyo?"
**Client**: Delegates to Eric → Eric uses Web Search → Returns current time

## 🔧 Customization

You can customize the client prompt by modifying the `instruction` parameter in `agent.py`:

- **Tone**: Adjust the friendliness level
- **Delegation rules**: Add more specific cases
- **Response format**: Specify how to present Eric's answers
- **Error handling**: Add instructions for handling failures

## 📊 Key Features

1. **Smart Delegation**: Automatically routes math questions to Eric
2. **Transparent Communication**: Users know when Eric is being consulted
3. **Comprehensive Coverage**: Handles math, science, and current information
4. **Robust Connection**: Uses retry configuration for reliability
5. **Clean Interface**: Simple, focused prompt that avoids confusion

## ⚙️ Configuration

The agent uses the following configuration:
- **Model**: `gemini-2.5-flash`
- **Retry attempts**: 5
- **Retry delay**: Exponential backoff (base 7)
- **HTTP status codes**: 429, 500, 503, 504

## 🎓 Prompt Engineering Principles Used

1. **Clear Role Definition**: Agent knows it's a client, not a solver
2. **Explicit Delegation Rules**: When to use Eric vs. handle directly
3. **Examples**: Concrete examples of each case
4. **Structured Format**: Sections with emojis for easy scanning
5. **Constraints**: Clear boundaries on what not to do
6. **Workflow**: Step-by-step process for consistency
7. **Best Practices**: Guidelines for quality interactions

## 🔍 Troubleshooting

### Connection Issues
- Ensure Eric server is running on port 8001
- Check network connectivity
- Verify the URL in `from_a2a` is correct

### Delegation Issues
- Review the delegation rules in the prompt
- Check if the question matches the examples
- Ensure Eric server is responding

### Response Quality
- Eric's response quality depends on his sub-agents
- Check Eric's logs for tool usage
- Verify the question is clear and specific
