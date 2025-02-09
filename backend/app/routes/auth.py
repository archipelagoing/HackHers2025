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
    scope="user-read-private user-read-email user-top-read playlist-modify-public user-follow-modify"
)

@router.get("/auth/login")
def login():
    """Generate Spotify authorization URL"""
    try:
        print("Generating Spotify auth URL...")
        print("Using credentials:", {
            "client_id": os.getenv("SPOTIFY_CLIENT_ID")[:8] + "...",
            "WWWWWWWWredirect_uri": os.getenv("SPOTIFY_REDIRECT_URI")
        })
        
        # Verify redirect URI is set and properly formatted
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        if not redirect_uri:
            raise HTTPException(
                status_code=500,
                detail="Redirect URI not configured"
            )
        
        # Clean any quotes from the redirect URI
        redirect_uri = redirect_uri.strip("'").strip('"')
        os.environ["SPOTIFY_REDIRECT_URI"] = redirect_uri
        
        print(f"Full redirect URI: {redirect_uri}")
        auth_url = sp_oauth.get_authorize_url()
        print(f"Auth URL generated: {auth_url}")
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"Error details: {type(e).__name__}: {str(e)}")
        print(f"Error generating auth URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/callback")
def spotify_callback(code: str):
    """Handle Spotify OAuth callback"""
    try:
        print(f"1. Received callback with code: {code[:10]}...")
        print(f"Full code: {code}")
        print(f"Using credentials:", {
            "client_id": os.getenv("SPOTIFY_CLIENT_ID")[:8] + "...",
            "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI")
        })
        
        token_info = sp_oauth.get_access_token(code)
        print("Token info received:", {
            "has_access_token": "access_token" in token_info,
            "has_refresh_token": "refresh_token" in token_info,
            "token_type": token_info.get("token_type"),
            "expires_in": token_info.get("expires_in")
        })
        
        sp = spotipy.Spotify(auth=token_info["access_token"])
        print("3. Created Spotify client")
        
        user_data = sp.current_user()
        print(f"4. Got user data for: {user_data.get('display_name')}")
        
        user_id = user_data["id"]
        username = user_data["display_name"]
        profile_pic = user_data["images"][0]["url"] if user_data["images"] else None
        
        print("5. Storing user data in Firestore...")
        # Store in Firestore
        db.collection("users").document(user_id).set({
            "username": username,
            "spotify_id": user_id,
            "profile_pic": profile_pic,
            "last_login": datetime.datetime.utcnow()
        }, merge=True)
        print("6. User data stored successfully")

        return {
            "message": "User authenticated", 
            "user_id": user_id,
            "access_token": token_info["access_token"]
        }
    except Exception as e:
        print(f"Error in callback: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this debug route to verify settings
@router.get("/auth/debug")
def debug_settings():
    return {
        "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI"),
        "client_id": os.getenv("SPOTIFY_CLIENT_ID")[:8] + "...",
        "scopes": sp_oauth.scope
    }




