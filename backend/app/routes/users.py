from fastapi import APIRouter, HTTPException, Depends, Header
from firebase_admin import firestore
from ..database import db
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from ..dependencies import get_spotify_oauth

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get a user's profile by their ID"""
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}")
async def create_user(user_id: str, user_data: dict):
    """Create or update a user's profile"""
    try:
        doc_ref = db.collection('users').document(user_id)
        doc_ref.set(user_data)
        return {"message": "User profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users():
    """Get all users (you might want to add pagination)"""
    try:
        users_ref = db.collection('users')
        docs = users_ref.stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user/top-artists")
def get_user_top_artists(user_id: str):
    """Gets user's top 10 artists and their genres"""
    sp = get_spotify_client(user_id)  # Get Spotify client with user's token
    top_artists = sp.current_user_top_artists(limit=10)["items"]
    
    # Extract artist names and genres
    artist_names = [artist["name"] for artist in top_artists]
    genres = list(set(genre for artist in top_artists for genre in artist["genres"]))
    
    # Store in Firebase
    db.collection("users").document(user_id).set({
        "top_artists": artist_names, 
        "genres": genres
    }, merge=True)

    return {"top_artists": artist_names, "genres": genres}

@router.get("/user/top-tracks")
def get_user_top_tracks(user_id: str):
    """Gets user's top 10 tracks"""
    sp = get_spotify_client(user_id)
    top_tracks = sp.current_user_top_tracks(limit=10)["items"]
    
    track_names = [track["name"] for track in top_tracks]
    track_ids = [track["id"] for track in top_tracks]  # Used for audio features

    db.collection("users").document(user_id).set({"top_tracks": track_names}, merge=True)

    return {"top_tracks": track_names, "track_ids": track_ids}

@router.get("/user/recent-tracks")
def get_user_recent_tracks(user_id: str):
    """Gets user's recently played tracks"""
    sp = get_spotify_client(user_id)
    recent_tracks = sp.current_user_recently_played(limit=10)["items"]
    
    track_names = [track["track"]["name"] for track in recent_tracks]
    track_ids = [track["track"]["id"] for track in recent_tracks]

    db.collection("users").document(user_id).set({"recent_tracks": track_names}, merge=True)

    return {"recent_tracks": track_names, "track_ids": track_ids}

@router.get("/user/audio-features")
def get_user_audio_features(user_id: str):
    """Fetch user's top tracks' audio features from Spotify and store in Firestore."""
    try:
        sp = get_spotify_client(user_id)
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            return {"error": "User not found"}

        track_ids = user_doc.to_dict().get("track_ids", [])
        if not track_ids:
            return {"error": "No top tracks found"}

        audio_features = sp.audio_features(track_ids)
        features_dict = {track["id"]: {
            "danceability": track["danceability"],
            "energy": track["energy"],
            "tempo": track["tempo"]
        } for track in audio_features if track}

        db.collection("users").document(user_id).set({"audio_features": features_dict}, merge=True)

        return {"audio_features": features_dict}
    except Exception as e:
        return {"error": str(e)}

def get_spotify_client(user_id: str):
    """Create a Spotify client for a specific user using their stored token"""
    try:
        # Get user's token from database
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise Exception("User not found")
        
        token = user_doc.to_dict().get("access_token")
        if not token:
            raise Exception("No access token found")
            
        # Create Spotify client with user's token
        return spotipy.Spotify(auth=token)
    except Exception as e:
        raise Exception(f"Failed to create Spotify client: {str(e)}")

@router.get("/me")
async def get_user_profile(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")
            
        token = authorization.replace('Bearer ', '')
        sp = Spotify(auth=token)
        
        # Get more user data
        user_profile = sp.current_user()
        top_artists = sp.current_user_top_artists(limit=5)
        top_tracks = sp.current_user_top_tracks(limit=5)
        playlists = sp.current_user_playlists(limit=5)
        
        # Extract genres
        all_genres = []
        for artist in top_artists['items']:
            all_genres.extend(artist['genres'])
        unique_genres = list(set(all_genres))[:5]
        
        return {
            "username": user_profile['display_name'],
            "spotify_id": user_profile['id'],
            "profile_image": user_profile['images'][0]['url'] if user_profile['images'] else None,
            "followers": user_profile['followers']['total'],
            "spotify_url": user_profile['external_urls']['spotify'],
            "top_artists": [artist['name'] for artist in top_artists['items']],
            "top_tracks": [{
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name'],
                "preview_url": track['preview_url']
            } for track in top_tracks['items']],
            "top_genres": unique_genres,
            "playlists": [{
                "name": playlist['name'],
                "tracks": playlist['tracks']['total'],
                "image": playlist['images'][0]['url'] if playlist['images'] else None
            } for playlist in playlists['items']]
        }
    except Exception as e:
        print(f"Error fetching user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user():
    """Get the current user's profile"""
    try:
        # Get user from Firestore
        users_ref = db.collection('users')
        # Get the most recently logged in user
        users = users_ref.order_by('last_login', direction='DESCENDING').limit(1).get()
        
        for user in users:
            user_data = user.to_dict()
            return {
                "username": user_data.get("username"),
                "spotify_id": user_data.get("spotify_id"),
                "profile_image": user_data.get("profile_image"),
                "top_artists": user_data.get("top_artists", []),
                "top_tracks": user_data.get("top_tracks", []),
                "top_genres": user_data.get("top_genres", [])
            }
            
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

