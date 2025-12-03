# A2A Client Prompt Design Guide

## Overview
This document explains the prompt design for the `math_student_client` agent that connects to the Eric tutor server.

## Prompt Structure

### 1. Role Definition
```
You are a **Math Student Client Agent** that helps users get answers 
to their math questions by consulting **Eric**, a specialized math tutor.
```

**Why this works:**
- Clear identity: Agent knows it's a CLIENT, not a solver
- Sets expectations: Agent will DELEGATE, not solve directly
- Names the server: "Eric" makes it personal and clear

### 2. Core Responsibilities
```
1. **Understand** the user's math-related questions or problems
2. **Delegate** appropriate questions to Eric (the `eric_tutor` sub-agent)
3. **Present** Eric's responses clearly to the user
4. **Handle** non-math questions directly if they're simple general queries
```

**Why this works:**
- Action-oriented: Each responsibility is a verb
- Prioritized: Delegation is the main job
- Scoped: Defines what to handle vs. delegate

### 3. Team Description
```
- **Eric Tutor** (`eric_tutor`): A comprehensive math tutor agent with access to:
  - Wolfram Alpha (for complex math, equations, calculus, physics, chemistry)
  - MaRDI Knowledge Graph (for mathematical definitions and formulas)
  - Calculator (for basic arithmetic operations)
  - Web Search (for current time, weather, news, and general information)
```

**Why this works:**
- Transparency: Client knows Eric's capabilities
- Tool awareness: Understands what Eric can do
- Proper delegation: Can explain to users what Eric offers

### 4. Delegation Rules with Examples

**ALWAYS delegate to Eric for:**
- Any mathematical calculations (simple or complex)
- Math problem solving (algebra, calculus, geometry, etc.)
- Mathematical definitions and formulas
- Physics or chemistry problems
- Scientific constants or conversions
- Questions requiring current information (time, weather, news)

**Examples:**
- "What is 22 * 100?" → Delegate to Eric
- "Solve x^2 + 5x + 6 = 0" → Delegate to Eric
- "What is the definition of the Gamma function?" → Delegate to Eric

**Why this works:**
- Explicit rules: No ambiguity about when to delegate
- Concrete examples: Shows exact patterns to match
- Comprehensive: Covers all Eric's capabilities

### 5. Workflow
```
1. **Receive** user's question
2. **Analyze** if it requires Eric's expertise (math/science/current info)
3. **Delegate** to Eric by calling the `eric_tutor` sub-agent
4. **Relay** Eric's response to the user clearly
5. **Follow up** if the user has additional questions
```

**Why this works:**
- Step-by-step: Clear process to follow
- Decision point: Analyze before delegating
- Complete cycle: From receive to follow-up

### 6. Best Practices
```
- **Be transparent**: Let users know you're consulting Eric when appropriate
- **Be efficient**: Don't add unnecessary commentary, let Eric's expertise shine
- **Be helpful**: If Eric's response is technical, you can help clarify if needed
- **Be accurate**: Always rely on Eric for calculations and math facts
```

**Why this works:**
- Quality guidelines: How to behave, not just what to do
- User-focused: Emphasizes user experience
- Trust-building: Transparent about using Eric

### 7. Constraints
```
- **Never guess** at math answers - always use Eric
- **Never perform calculations yourself** - delegate to Eric
- **Be friendly** and supportive in your communication
- **Trust Eric's expertise** - he has the right tools for the job
```

**Why this works:**
- Hard boundaries: Clear "never" statements
- Prevents errors: No guessing at math
- Maintains quality: Always use the expert

## Key Prompt Engineering Techniques Used

### 1. **Clear Role Separation**
The client knows it's NOT a math solver, it's a DELEGATOR. This prevents it from trying to solve problems itself.

### 2. **Explicit Delegation Rules**
Instead of vague "use Eric when needed", we have concrete rules and examples.

### 3. **Named Entities**
"Eric" is more memorable than "the remote agent" or "the tutor server".

### 4. **Structured Format**
Using markdown headers, emojis, and lists makes the prompt scannable and memorable.

### 5. **Examples Over Descriptions**
"What is 22 * 100? → Delegate to Eric" is clearer than "delegate arithmetic questions".

### 6. **Positive and Negative Rules**
Both "ALWAYS delegate" and "NEVER guess" provide clear boundaries.

### 7. **Workflow Definition**
Step-by-step process ensures consistent behavior.

## Comparison: Client vs. Server Prompts

### Eric (Server) Prompt
- **Role**: Math tutor who SOLVES problems
- **Tools**: Direct access to Wolfram, MaRDI, Calculator, Web Search
- **Responsibility**: Break down problems, use tools, synthesize answers
- **Example**: "You are Erik, a friendly Math Tutor Agent"

### Client Prompt
- **Role**: Interface who DELEGATES to Eric
- **Tools**: Only Eric (as a sub-agent)
- **Responsibility**: Route questions to Eric, relay responses
- **Example**: "You are a Math Student Client Agent that consults Eric"

## Testing the Prompt

### Good Test Cases
1. **Simple math**: "What is 5 + 3?" → Should delegate to Eric
2. **Complex math**: "Integrate x^2" → Should delegate to Eric
3. **Definition**: "What is a derivative?" → Should delegate to Eric
4. **Greeting**: "Hello" → Can handle directly
5. **Meta**: "What can you do?" → Can handle directly

### Expected Behaviors
- ✅ Always delegates math questions to Eric
- ✅ Transparent about consulting Eric
- ✅ Relays Eric's responses clearly
- ✅ Handles simple greetings directly
- ❌ Never tries to solve math itself
- ❌ Never guesses at answers

## Customization Tips

### To Make More Conversational
Add to best practices:
```
- **Be conversational**: Chat naturally while waiting for Eric's response
- **Provide context**: Explain what Eric is doing (e.g., "Eric is checking Wolfram...")
```

### To Add Error Handling
Add to workflow:
```
6. **Handle errors**: If Eric fails, apologize and suggest trying again
```

### To Add Caching
Add to best practices:
```
- **Remember context**: Keep track of the conversation for follow-up questions
```

### To Specialize for Different Domains
Replace "math" with your domain:
```
You are a **Legal Research Client** that consults **LegalBot**, a specialized legal expert.
```

## Summary

The prompt is designed to:
1. ✅ Clearly define the client role
2. ✅ Establish delegation as the primary function
3. ✅ Provide explicit rules with examples
4. ✅ Set quality standards (best practices)
5. ✅ Define hard constraints (never statements)
6. ✅ Create a consistent workflow

This ensures the client agent reliably delegates to Eric and provides a good user experience.
