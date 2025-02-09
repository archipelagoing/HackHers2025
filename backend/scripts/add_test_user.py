from google.cloud import firestore
from datetime import datetime

def add_test_user():
    # Initialize Firestore client
    db = firestore.Client()
    
    # Test user data with similar genres to match with your profile
    test_user = {
        "spotify_id": "test_user_1",
        "username": "Music Lover",
        "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",  # Sample Spotify image
        "top_artists": [
            "The Beatles",
            "Pink Floyd",
            "Led Zeppelin",
            "Radiohead",
            "Arctic Monkeys"
        ],
        "top_genres": [
            "rock",
            "indie rock",
            "alternative rock",
            "classic rock",
            "psychedelic rock"
        ],
        "last_updated": datetime.now()
    }
    
    # Add more test users with varying match percentages
    test_users = [
        {
            "spotify_id": "test_user_2",
            "username": "Jazz Cat",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": ["Miles Davis", "John Coltrane", "Ella Fitzgerald"],
            "top_genres": ["jazz", "bebop", "swing", "classical", "blues"],
            "last_updated": datetime.now()
        },
        {
            "spotify_id": "test_user_3",
            "username": "Genre Mixer",
            "profile_image": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
            "top_artists": ["Radiohead", "Miles Davis", "Aphex Twin"],
            "top_genres": ["electronic", "rock", "jazz", "ambient", "experimental"],
            "last_updated": datetime.now()
        }
    ]
    
    try:
        # Add main test user
        db.collection('users').document(test_user['spotify_id']).set(test_user)
        print(f"Added test user: {test_user['username']}")
        
        # Add additional test users
        for user in test_users:
            db.collection('users').document(user['spotify_id']).set(user)
            print(f"Added test user: {user['username']}")
            
        print("Successfully added all test users!")
        
    except Exception as e:
        print(f"Error adding test users: {str(e)}")

if __name__ == "__main__":
    add_test_user() 