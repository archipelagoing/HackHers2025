# scripts/add_test_users.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

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
db = firestore.client()

# Test user data with more diverse music tastes
test_users = [
    {
        "id": "user_pop_1",
        "username": "PopLover",
        "top_artists": ["Drake", "The Weeknd", "Doja Cat", "Post Malone", "Travis Scott"],
        "audio_features": {
            "danceability": 0.8,
            "energy": 0.75,
            "valence": 0.65,
            "tempo": 128,
            "instrumentalness": 0.1
        }
    },
    {
        "id": "match_1",
        "username": "RnBSoul",
        "top_artists": ["The Weeknd", "Drake", "SZA", "Post Malone", "Frank Ocean"],
        "audio_features": {
            "danceability": 0.75,
            "energy": 0.7,
            "valence": 0.6,
            "tempo": 125,
            "instrumentalness": 0.15
        }
    },
    {
        "id": "match_2",
        "username": "HipHopHeart",
        "top_artists": ["Travis Scott", "Drake", "Kendrick Lamar", "Post Malone", "21 Savage"],
        "audio_features": {
            "danceability": 0.85,
            "energy": 0.8,
            "valence": 0.7,
            "tempo": 130,
            "instrumentalness": 0.1
        }
    },
    {
        "id": "match_3",
        "username": "PopPrincess",
        "top_artists": ["Doja Cat", "The Weeknd", "Ariana Grande", "Drake", "Dua Lipa"],
        "audio_features": {
            "danceability": 0.8,
            "energy": 0.75,
            "valence": 0.65,
            "tempo": 128,
            "instrumentalness": 0.1
        }
    },
    {
        "id": "user_pop_2",
        "username": "PopStar",
        "top_artists": ["Drake", "Ariana Grande", "The Weeknd", "Dua Lipa", "Bad Bunny"],
        "audio_features": {
            "danceability": 0.75,
            "energy": 0.7,
            "valence": 0.7,
            "tempo": 125,
            "instrumentalness": 0.15
        }
    },
    {
        "id": "user_metal",
        "username": "MetalHead",
        "top_artists": ["Metallica", "Slipknot", "System of a Down", "Tool", "Rammstein"],
        "audio_features": {
            "danceability": 0.4,
            "energy": 0.9,
            "valence": 0.3,
            "tempo": 140,
            "instrumentalness": 0.3
        }
    },
    {
        "id": "user_indie_1",
        "username": "IndieSoul",
        "top_artists": ["Arctic Monkeys", "The Strokes", "Tame Impala", "The 1975", "Vampire Weekend"],
        "audio_features": {
            "danceability": 0.65,
            "energy": 0.7,
            "valence": 0.6,
            "tempo": 122,
            "instrumentalness": 0.25
        }
    },
    {
        "id": "user_indie_2",
        "username": "IndieVibes",
        "top_artists": ["Tame Impala", "Mac DeMarco", "MGMT", "Arctic Monkeys", "Beach House"],
        "audio_features": {
            "danceability": 0.6,
            "energy": 0.65,
            "valence": 0.55,
            "tempo": 120,
            "instrumentalness": 0.3
        }
    },
    {
        "id": "user_classical",
        "username": "ClassicalSoul",
        "top_artists": ["Ludwig van Beethoven", "Wolfgang Amadeus Mozart", "Johann Sebastian Bach", "Frédéric Chopin", "Claude Debussy"],
        "audio_features": {
            "danceability": 0.25,
            "energy": 0.45,
            "valence": 0.5,
            "tempo": 95,
            "instrumentalness": 0.95
        }
    },
    {
        "id": "user_electronic",
        "username": "ElectronicDreams",
        "top_artists": ["Daft Punk", "Deadmau5", "Aphex Twin", "Chemical Brothers", "Boards of Canada"],
        "audio_features": {
            "danceability": 0.85,
            "energy": 0.9,
            "valence": 0.7,
            "tempo": 135,
            "instrumentalness": 0.8
        }
    }
]

def add_test_users():
    """Add test users to Firestore"""
    for user in test_users:
        user_id = user.pop('id')  # Remove and get the ID
        try:
            db.collection('users').document(user_id).set(user)
            print(f"Added test user: {user_id}")
        except Exception as e:
            print(f"Error adding user {user_id}: {e}")

if __name__ == "__main__":
    add_test_users()
    print("Test users added successfully!")