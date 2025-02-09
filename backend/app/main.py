import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, match, ai_claude  # Remove playlists if not using yet
from .dependencies import get_spotify_oauth  # Add this
from spotipy import Spotify
from google.cloud import firestore
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI()

# Add health check endpoint first
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# Get Spotify OAuth instance
sp_oauth = get_spotify_oauth()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Each route has a prefix and tags for Swagger docs
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(match.router, prefix="/match", tags=["match"])
app.include_router(ai_claude.router, prefix="/ai", tags=["ai"])
# app.include_router(playlists.router, prefix="/playlists", tags=["playlists"])  # Comment if not using

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}
