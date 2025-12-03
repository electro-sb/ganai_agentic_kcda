"""
Example usage of the a2a_client agent that connects to Eric tutor server.

This script demonstrates how to:
1. Import the client agent
2. Create a runner
3. Send questions to Eric via the client
4. Display responses
"""

from agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import uuid

def main():
    # Create a session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
    )
    
    # Create a session ID
    session_id = str(uuid.uuid4())
    
    print("=" * 60)
    print("Math Student Client - Connected to Eric Tutor")
    print("=" * 60)
    print("\nThis client connects to Eric, a math tutor with access to:")
    print("  • Wolfram Alpha (complex math)")
    print("  • MaRDI Knowledge Graph (definitions)")
    print("  • Calculator (basic arithmetic)")
    print("  • Web Search (current information)")
    print("\n" + "=" * 60)
    
    # Example questions to test
    example_questions = [
        "What is 22 * 100?",
        "Solve x^2 + 5x + 6 = 0",
        "What is the definition of the Gamma function?",
        "Integrate sin(x) from 0 to pi",
    ]
    
    print("\n🎓 Example Questions:\n")
    for i, question in enumerate(example_questions, 1):
        print(f"{i}. {question}")
    
    print("\n" + "=" * 60)
    print("\n💬 Interactive Mode - Type 'quit' to exit\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Send to the client agent
            print("\n🤖 Client: Consulting Eric...\n")
            
            response = runner.run(
                session_id=session_id,
                user_message=user_input,
            )
            
            # Display response
            print(f"Eric: {response.content}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Make sure the Eric tutor server is running on port 8001!")
            print("Start it with: cd ../a2a_tutor_serv && python agent.py\n")

if __name__ == "__main__":
    print("\n🚀 Starting Math Student Client...")
    print("📡 Connecting to Eric Tutor Server (http://localhost:8001)...\n")
    
    try:
        main()
    except Exception as e:
        print(f"\n❌ Failed to start client: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Eric server is running: cd ../a2a_tutor_serv && python agent.py")
        print("2. Check that port 8001 is available")
        print("3. Verify your .env file has the correct API keys")
