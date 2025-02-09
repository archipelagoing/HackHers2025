import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import os
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

def add_archipelagoing_matches():
    test_users = [
        {
            "spotify_id": "match_indie_1",
            "username": "Indie Dream Pop Fan",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": [
                "Clairo",
                "Japanese Breakfast",
                "Lorde",
                "Phoebe Bridgers",
                "The 1975",
                "Beach House",
                "Weyes Blood",
                "Men I Trust"
            ],
            "top_tracks": [
                "Nobody",
                "Be Sweet",
                "Motion Sickness",
                "Second Nature",
                "Nomad",
                "Space Song",
                "And It Breaks My Heart",
                "Show Me How"
            ],
            "top_genres": [
                "indie pop",
                "art pop",
                "dream pop",
                "indie rock",
                "indie folk",
                "bedroom pop",
                "alternative"
            ],
            "audio_features": {
                "danceability": 0.65,
                "energy": 0.70,
                "valence": 0.55
            },
            "last_updated": datetime.now()
        },
        {
            "spotify_id": "match_alt_2",
            "username": "Alt Pop Enthusiast",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": [
                "Lorde",
                "Taylor Swift",
                "The 1975",
                "Arctic Monkeys",
                "Lana Del Rey",
                "Florence + The Machine",
                "FKA twigs",
                "HAIM"
            ],
            "top_tracks": [
                "Solar Power",
                "Cruel Summer",
                "If You're Too Shy (Let Me Know)",
                "Do I Wanna Know?",
                "Video Games",
                "Dog Days Are Over",
                "cellophane",
                "The Wire"
            ],
            "top_genres": [
                "art pop",
                "indie pop",
                "alternative",
                "pop",
                "indie rock",
                "electropop",
                "dream pop"
            ],
            "audio_features": {
                "danceability": 0.68,
                "energy": 0.75,
                "valence": 0.60
            },
            "last_updated": datetime.now()
        },
        {
            "spotify_id": "match_dream_3",
            "username": "Dream Pop Lover",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": [
                "Beach House",
                "Men I Trust",
                "Weyes Blood",
                "Japanese Breakfast",
                "Mitski",
                "Alvvays",
                "Cocteau Twins",
                "Mazzy Star"
            ],
            "top_tracks": [
                "Space Song",
                "Show Me How",
                "Andromeda",
                "Be Sweet",
                "Nobody",
                "Archie, Marry Me",
                "Cherry-coloured Funk",
                "Fade Into You"
            ],
            "top_genres": [
                "dream pop",
                "indie pop",
                "shoegaze",
                "indie rock",
                "art pop",
                "bedroom pop",
                "ambient pop"
            ],
            "audio_features": {
                "danceability": 0.55,
                "energy": 0.65,
                "valence": 0.50
            },
            "last_updated": datetime.now()
        }
    ]
    
    try:
        # Add all test users to Firestore
        for user in test_users:
            db.collection('users').document(user['spotify_id']).set(user)
            print(f"Added match: {user['username']}")
            print(f"Artists: {', '.join(user['top_artists'][:3])}...")
            print(f"Genres: {', '.join(user['top_genres'][:3])}...")
            print("---")
            
        print(f"Successfully added {len(test_users)} matches!")
        
    except Exception as e:
        print(f"Error adding matches: {str(e)}")

if __name__ == "__main__":
    add_archipelagoing_matches() 