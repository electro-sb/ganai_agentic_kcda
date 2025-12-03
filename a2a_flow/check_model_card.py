import requests
import json

def check_model_card():
    #------------------------------------------------------------------
    # Fetch the agent card from the running server
    #------------------------------------------------------------------
    try:
        response = requests.get(
            "http://localhost:8001/.well-known/agent-card.json", timeout=5
        )

        if response.status_code == 200:
            agent_card = response.json()
            print("📋 Product Catalog Agent Card:")
            print(json.dumps(agent_card, indent=2))

            print("\n✨ Key Information:")
            print(f"   Name: {agent_card.get('name')}")
            print(f"   Description: {agent_card.get('description')}")
            print(f"   URL: {agent_card.get('url')}")
            print(f"   Skills: {len(agent_card.get('skills', []))} capabilities exposed")
        else:
            print(f"❌ Failed to fetch agent card: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching agent card: {e}")
        print("   Make sure the Product Catalog Agent server is running (previous cell)")

if __name__ == "__main__":
    check_model_card()
    