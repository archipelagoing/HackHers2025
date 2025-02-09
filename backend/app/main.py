import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, match, ai_claude  # Remove playlists if not using yet
from spotipy.oauth2 import SpotifyOAuth  # Add this import

# Load environment variables
load_dotenv()

app = FastAPI()

# Add Spotify OAuth configuration
sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope="user-read-private user-read-email"
)

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
        print("Generating Spotify auth URL...")  # Debug log
        auth_url = sp_oauth.get_authorize_url()
        print(f"Auth URL generated: {auth_url}")  # Debug log
        print("Full response being sent:", {"auth_url": auth_url})  # Debug full response
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"Error generating auth URL: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback")
async def spotify_callback(code: str):
    try:
        print(f"Received callback with code: {code}")  # Debug log
        token_info = sp_oauth.get_access_token(code)
        return token_info
    except Exception as e:
        print(f"Callback error: {str(e)}")  # Debug log
        raise HTTPException(status_code=400, detail=str(e))
