import os
import datetime
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
#from fastapi.sessions import SessionMiddleware
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from ..database import db

# Load environment variables
load_dotenv()

router = APIRouter()

# Spotify authentication setup
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-top-read playlist-modify-public user-follow-modify"
)

@router.get("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

@router.get("/callback")
def spotify_callback(code: str):
    """Handle Spotify OAuth callback and fetch user profile data."""
    try:
        token_info = sp_oauth.get_access_token(code)
        sp = spotipy.Spotify(auth=token_info["access_token"])
        user_data = sp.current_user()
        
        user_id = user_data["id"]
        username = user_data["display_name"]
        profile_pic = user_data["images"][0]["url"] if user_data["images"] else None
        
        # Store in Firestore
        db.collection("users").document(user_id).set({
            "username": username,
            "spotify_id": user_id,
            "profile_pic": profile_pic,
            "last_login": datetime.datetime.utcnow()
        }, merge=True)

        return {
            "message": "User authenticated", 
            "user_id": user_id,
            "access_token": token_info["access_token"]
        }
    except Exception as e:
        return {"error": str(e)}

