import os
import requests
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase with credentials from environment variables
cred_dict = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token",
}

# Initialize Firebase
cred = credentials.Certificate(cred_dict)
initialize_app(cred)
db = firestore.client()

def setup_test_users():
    """Create or update test users with required data"""
    test_users = {
        "user_pop_1": {
            "top_artists": ["Taylor Swift", "Ed Sheeran", "Ariana Grande"],
            "top_tracks": ["Shake It Off", "Shape of You", "7 Rings"],
            "top_genres": ["pop", "dance pop", "pop rock"],
            "audio_features": {
                "danceability": 0.8,
                "energy": 0.7,
                "valence": 0.6
            }
        },
        "match_1": {
            "top_artists": ["Taylor Swift", "The Weeknd", "Drake"],
            "top_tracks": ["Shake It Off", "Blinding Lights", "God's Plan"],
            "top_genres": ["pop", "r&b", "hip hop"],
            "audio_features": {
                "danceability": 0.75,
                "energy": 0.8,
                "valence": 0.65
            }
        },
        "match_2": {
            "top_artists": ["Ed Sheeran", "Justin Bieber", "Post Malone"],
            "top_tracks": ["Perfect", "Stay", "Circles"],
            "top_genres": ["pop", "pop rock", "trap"],
            "audio_features": {
                "danceability": 0.7,
                "energy": 0.6,
                "valence": 0.5
            }
        },
        "match_3": {
            "top_artists": ["Ariana Grande", "Doja Cat", "Dua Lipa"],
            "top_tracks": ["7 Rings", "Say So", "Levitating"],
            "top_genres": ["pop", "dance pop", "r&b"],
            "audio_features": {
                "danceability": 0.85,
                "energy": 0.75,
                "valence": 0.7
            }
        }
    }
    
    # Update or create users in Firestore
    for user_id, user_data in test_users.items():
        db.collection('users').document(user_id).set(user_data, merge=True)
        print(f"Updated user: {user_id}")

def test_matches():
    base_url = "http://localhost:8000/match/match"
    user1 = "user_pop_1"
    matches = ["match_1", "match_2", "match_3"]
    
    for match in matches:
        data = {
            "user1_spotify_id": user1,
            "user2_spotify_id": match
        }
        
        try:
            response = requests.post(base_url, json=data)
            print(f"\nMatch with {match}:")
            if response.status_code == 200:
                print(response.json())
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error testing match: {e}")

if __name__ == "__main__":
    print("Setting up test users...")
    setup_test_users()
    print("\nTesting matches...")
    test_matches() 