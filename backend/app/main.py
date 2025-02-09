import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, match, ai_claude  # Remove playlists if not using yet
from .dependencies import get_spotify_oauth  # Add this
from spotipy import Spotify
from google.cloud import firestore

# Load environment variables
load_dotenv()

app = FastAPI()

# Get Spotify OAuth instance
sp_oauth = get_spotify_oauth()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Each route has a prefix and tags for Swagger docs
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(match.router, prefix="/match", tags=["match"])
app.include_router(ai_claude.router, prefix="/ai", tags=["ai"])
# app.include_router(playlists.router, prefix="/playlists", tags=["playlists"])  # Comment if not using

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}

@auth.router.get("/login")
def login():
    try:
        print("Generating Spotify auth URL...")
        auth_url = sp_oauth.get_authorize_url()  # Generate Spotify URL
        print(f"Auth URL generated: {auth_url}")
        return {"auth_url": auth_url}  # Send URL back to frontend
    except Exception as e:
        print(f"Error generating auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback")
async def spotify_callback(code: str):
    try:
        print(f"Received callback with code: {code}")
        token_info = sp_oauth.get_access_token(code)
        
        # Create Spotify client with new token
        sp = Spotify(auth=token_info['access_token'])
        
        # Get user data
        user_profile = sp.current_user()
        top_artists = sp.current_user_top_artists(limit=10)
        
        # Extract genres
        all_genres = []
        for artist in top_artists['items']:
            all_genres.extend(artist['genres'])
        unique_genres = list(set(all_genres))[:5]
        
        # Store user data in Firebase
        user_data = {
            "spotify_id": user_profile['id'],
            "username": user_profile['display_name'],
            "profile_image": user_profile['images'][0]['url'] if user_profile['images'] else None,
            "top_artists": [artist['name'] for artist in top_artists['items']],
            "top_genres": unique_genres,
            "last_updated": firestore.SERVER_TIMESTAMP
        }
        
        # Save to Firebase
        db = firestore.Client()
        db.collection('users').document(user_profile['id']).set(user_data, merge=True)
        print(f"Stored user data for: {user_profile['display_name']}")
        
        return token_info
        
    except Exception as e:
        print(f"Callback error details: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
