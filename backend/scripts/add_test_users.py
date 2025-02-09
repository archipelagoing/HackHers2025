# scripts/add_test_users.py
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get Firebase credentials from environment variables
cred_dict = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token",
}

# Initialize Firebase
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

def add_test_users():
    test_users = [
        {
            "spotify_id": "test_match_1",
            "username": "Indie Pop Lover",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": [
                "Lorde",
                "Taylor Swift",
                "Mitski",
                "Phoebe Bridgers",
                "Japanese Breakfast",
                "The 1975",
                "Arctic Monkeys",
                "Lana Del Rey"
            ],
            "top_tracks": [
                "Solar Power",
                "Cruel Summer",
                "Motion Sickness",
                "I Know The End",
                "Be Sweet",
                "Somebody Else",
                "505",
                "Video Games"
            ],
            "top_genres": [
                "indie pop",
                "art pop",
                "indie rock",
                "alternative",
                "bedroom pop",
                "indie folk",
                "dream pop"
            ],
            "audio_features": {
                "danceability": 0.65,
                "energy": 0.70,
                "valence": 0.55
            },
            "last_updated": datetime.now()
        },
        {
            "spotify_id": "test_match_2",
            "username": "Alternative Vibes",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": [
                "Arctic Monkeys",
                "The Strokes",
                "Tame Impala",
                "Mitski",
                "The 1975",
                "Lorde",
                "Beach House",
                "Mac DeMarco"
            ],
            "top_tracks": [
                "505",
                "Do I Wanna Know?",
                "The Less I Know The Better",
                "Your Best American Girl",
                "Somebody Else",
                "Green Light",
                "Space Song",
                "Chamber of Reflection"
            ],
            "top_genres": [
                "indie rock",
                "alternative",
                "psychedelic rock",
                "art pop",
                "dream pop",
                "indie pop",
                "bedroom pop"
            ],
            "audio_features": {
                "danceability": 0.60,
                "energy": 0.75,
                "valence": 0.50
            },
            "last_updated": datetime.now()
        }
    ]
    
    try:
        # Add all test users to Firestore
        for user in test_users:
            db.collection('users').document(user['spotify_id']).set(user)
            print(f"Added test user: {user['username']} with genres: {', '.join(user['top_genres'])}")
            
        print(f"Successfully added {len(test_users)} test users!")
        
    except Exception as e:
        print(f"Error adding test users: {str(e)}")

if __name__ == "__main__":
    add_test_users()