import os
from fastapi import APIRouter
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# Spotify authentication setup
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-top-read playlist-modify-public user-follow-modify"
)

@router.get("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

@router.get("/callback")
def callback(code: str):
    token_info = sp_oauth.get_access_token(code)
    return {"access_token": token_info["access_token"]}
