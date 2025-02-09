import requests
import json

BASE_URL = "http://localhost:8000/ai"

def test_claude_endpoints():
    # Test basic prompt
    print("\n1. Testing basic Claude prompt...")
    response = requests.get(f"{BASE_URL}/test-claude", params={
        "prompt": "Write a short poem about music"
    })
    print("Response:", json.dumps(response.json(), indent=2))

    # Test personality bio
    print("\n2. Testing personality bio generation...")
    response = requests.get(f"{BASE_URL}/claude-personality-bio", params={
        "user_id": "archisa28"  # Replace with actual user ID
    })
    print("Response:", json.dumps(response.json(), indent=2))

    # Test shared playlist
    print("\n3. Testing shared playlist generation...")
    response = requests.get(f"{BASE_URL}/claude-shared-playlist", params={
        "user1_id": "archisa28",  # Replace with actual user IDs
        "user2_id": "match_indie_1"
    })
    print("Response:", json.dumps(response.json(), indent=2))

    # Test match description
    print("\n4. Testing match description...")
    response = requests.get(f"{BASE_URL}/claude-match-description", params={
        "user1_id": "archisa28",  # Replace with actual user IDs
        "user2_id": "match_indie_1"
    })
    print("Response:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_claude_endpoints() 