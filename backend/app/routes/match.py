from typing import Dict, List, Tuple
import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User  # You'll need to create this model
from datetime import datetime, timedelta
import base64

# ============================
# 🎵 SPOTIFY API CONFIGURATION 🎵
# ============================
load_dotenv()  # Load environment variables from .env file

SPOTIFY_API_BASE = "https://api.spotify.com/v1"
AUTH_URL = "https://accounts.spotify.com/api/token"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Missing Spotify API credentials in environment variables")


def get_access_token(refresh_token: str) -> str:
    """
    Refresh the Spotify API access token using OAuth.
    """
    response = requests.post(
        AUTH_URL,
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        headers={"Authorization": f"Basic {requests.auth._basic_auth_str(CLIENT_ID, CLIENT_SECRET)}"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    raise Exception("Failed to refresh access token.")


def make_spotify_request(endpoint: str, access_token: str, params=None) -> Dict:
    """
    Make an authenticated request to Spotify API.
    """
    response = requests.get(
        f"{SPOTIFY_API_BASE}{endpoint}",
        headers={"Authorization": f"Bearer {access_token}"},
        params=params
    )
    
    if response.status_code == 401:
        raise Exception("Access token expired. Please refresh.")
    
    return response.json()


# ============================
# 🎵 FETCH USER SPOTIFY DATA 🎵
# ============================

def get_user_top_artists(access_token: str, limit=5) -> Tuple[List[str], List[str]]:
    """
    Fetch user's top artists and their genres.
    """
    endpoint = "/me/top/artists"
    params = {"limit": limit}
    data = make_spotify_request(endpoint, access_token, params)

    artist_names = [artist["name"] for artist in data.get("items", [])]
    genres = list(set(genre for artist in data.get("items", []) for genre in artist.get("genres", [])))

    return artist_names, genres


def get_user_top_tracks(access_token: str, limit=5) -> List[str]:
    """
    Fetch user's top tracks.
    """
    endpoint = "/me/top/tracks"
    params = {"limit": limit}
    data = make_spotify_request(endpoint, access_token, params)
    return [track["name"] for track in data.get("items", [])]


def get_user_recent_tracks(access_token: str, limit=5) -> List[str]:
    """
    Fetch user's recently played tracks.
    """
    endpoint = "/me/player/recently-played"
    params = {"limit": limit}
    data = make_spotify_request(endpoint, access_token, params)
    return [track["track"]["name"] for track in data.get("items", [])]


def get_audio_features(track_ids: List[str], access_token: str) -> np.ndarray:
    """
    Fetch audio features for multiple track IDs in batches.
    """
    features = []
    # Process in batches of 100
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        endpoint = f"/audio-features"
        data = make_spotify_request(endpoint, access_token, params={"ids": ",".join(batch)})
        
        for track_features in data.get("audio_features", []):
            if track_features:  # Check if features exist
                features.append([
                    track_features.get("danceability", 0),
                    track_features.get("energy", 0),
                    track_features.get("valence", 0)
                ])
    
    return np.array(features) if features else np.array([])


# ============================
# 🎵 MATCHING ALGORITHM 🎵
# ============================

class MatchStrength(str, Enum):
    PERFECT = "PERFECT"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    NO_MATCH = "NO_MATCH"


@dataclass
class MatchScore:
    total_score: float
    artist_score: float
    track_score: float
    genre_score: float
    recent_score: float
    audio_score: float
    shared_items: Dict
    strength: MatchStrength
    compatibility_reasons: List[str]


class FlirtifyMatcher:
    def __init__(self):
        self.weights = {
            'exact_artist_match': 30,
            'exact_track_match': 20,
            'genre_match': 15,
            'recent_activity_bonus': 10,
            'audio_features_similarity': 25
        }
        self.thresholds = {
            'perfect': 90,
            'strong': 70,
            'moderate': 50,
            'weak': 30
        }

    def match_users(self, user1_token: str, user2_token: str) -> Dict:
        # Get data for both users
        user1_data = self._get_user_music_data(user1_token)
        user2_data = self._get_user_music_data(user2_token)
        
        # Calculate scores
        scores = {
            'artists': self._calculate_artist_score(user1_data['artists'], user2_data['artists']),
            'tracks': self._calculate_track_score(user1_data['tracks'], user2_data['tracks']),
            'genres': self._calculate_genre_score(user1_data['genres'], user2_data['genres']),
            'recent': self._calculate_recent_score(user1_data['recent'], user2_data['recent']),
            'audio': self._calculate_audio_similarity(user1_data['audio_features'], user2_data['audio_features'])
        }
        
        # Get shared items
        shared_items = {
            'artists': list(set(user1_data['artists']) & set(user2_data['artists'])),
            'genres': list(set(user1_data['genres']) & set(user2_data['genres'])),
            'tracks': list(set(user1_data['tracks']) & set(user2_data['tracks']))
        }
        
        # Evaluate match strength and get reasons
        strength, reasons = self._evaluate_match_strength(scores, shared_items)
        
        return {
            'total_score': sum(scores.values()),
            'strength': strength,
            'reasons': reasons,
            'shared_items': shared_items
        }

    def _get_user_music_data(self, token: str) -> Dict:
        artists, genres = get_user_top_artists(token)
        tracks = get_user_top_tracks(token)
        recent = get_user_recent_tracks(token)
        audio_features = get_audio_features([t['id'] for t in tracks], token)
        
        return {
            'artists': artists,
            'genres': genres,
            'tracks': tracks,
            'recent': recent,
            'audio_features': audio_features
        }

    def _calculate_artist_score(self, user1_artists: List[str], user2_artists: List[str]) -> float:
        return len(set(user1_artists) & set(user2_artists)) * self.weights['exact_artist_match']

    def _calculate_track_score(self, user1_tracks: List[str], user2_tracks: List[str]) -> float:
        return len(set(user1_tracks) & set(user2_tracks)) * self.weights['exact_track_match']

    def _calculate_genre_score(self, user1_genres: List[str], user2_genres: List[str]) -> float:
        return len(set(user1_genres) & set(user2_genres)) * self.weights['genre_match']

    def _calculate_recent_score(self, user1_recent: List[str], user2_recent: List[str]) -> float:
        return len(set(user1_recent) & set(user2_recent)) * self.weights['recent_activity_bonus']

    def _calculate_audio_similarity(self, user1_features: np.ndarray, user2_features: np.ndarray) -> float:
        if user1_features.size == 0 or user2_features.size == 0:
            return 0.0

        similarity_matrix = cosine_similarity(user1_features, user2_features)
        return np.mean(similarity_matrix) * self.weights["audio_features_similarity"]

    def _evaluate_match_strength(self, scores: Dict, shared_items: Dict) -> Tuple[MatchStrength, List[str]]:
        total_score = sum(scores.values())
        
        # Determine strength
        if total_score >= self.thresholds['perfect']:
            strength = MatchStrength.PERFECT
        elif total_score >= self.thresholds['strong']:
            strength = MatchStrength.STRONG
        elif total_score >= self.thresholds['moderate']:
            strength = MatchStrength.MODERATE
        elif total_score >= self.thresholds['weak']:
            strength = MatchStrength.WEAK
        else:
            strength = MatchStrength.NO_MATCH
        
        # Generate reasons
        reasons = []
        if shared_items['artists']:
            reasons.append(f"You both love {', '.join(shared_items['artists'][:2])}")
        if shared_items['genres']:
            reasons.append(f"You share interests in {', '.join(shared_items['genres'][:2])}")
        if shared_items['tracks']:
            reasons.append(f"You both enjoy {', '.join(shared_items['tracks'][:2])}")
        if scores['audio'] > 0:
            reasons.append("Your music taste has similar emotional qualities")
            
        return strength, reasons


# ============================
# 🎵 MATCH USERS FUNCTION 🎵
# ============================

def match_users(user1_token: str, user2_token: str):
    """
    Match two users based on their Spotify data.
    """
    matcher = FlirtifyMatcher()

    user1_top_artists, user1_genres = get_user_top_artists(user1_token)
    user2_top_artists, user2_genres = get_user_top_artists(user2_token)

    user1_data = {"top_artists": user1_top_artists, "genres": user1_genres, "top_tracks": get_user_top_tracks(user1_token)}
    user2_data = {"top_artists": user2_top_artists, "genres": user2_genres, "top_tracks": get_user_top_tracks(user2_token)}

    match_result = matcher.match_users(user1_token, user2_token)
    
    print(f"Match Strength: {match_result['strength'].value}")
    print(f"Total Score: {match_result['total_score']:.2f}/100")

# Example Usage
# match_users("user1_access_token", "user2_access_token")

router = APIRouter()

class MatchRequest(BaseModel):
    user1_spotify_id: str
    user2_spotify_id: str

class MatchResponse(BaseModel):
    match_score: float
    match_strength: str
    compatibility_reasons: List[str]
    shared_artists: List[str]
    shared_genres: List[str]
    shared_tracks: List[str]

async def get_user_token(spotify_id: str, db: Session = Depends(get_db)) -> str:
    user = db.query(User).filter(User.spotify_id == spotify_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User with Spotify ID {spotify_id} not found")
    
    if is_token_expired(user.token_expiry):
        new_token = get_access_token(user.refresh_token)
        user.access_token = new_token
        user.token_expiry = calculate_expiry()
        db.commit()
        return new_token
        
    return user.access_token

def is_token_expired(expiry_time) -> bool:
    return datetime.utcnow() + timedelta(seconds=60) >= expiry_time

def calculate_expiry() -> datetime:
    return datetime.utcnow() + timedelta(hours=1)

@router.post("/match", response_model=MatchResponse)
async def match_users(request: MatchRequest, db: Session = Depends(get_db)):
    try:
        # Get access tokens for both users
        user1_token = await get_user_token(request.user1_spotify_id, db)
        user2_token = await get_user_token(request.user2_spotify_id, db)
        
        matcher = FlirtifyMatcher()
        match_result = matcher.match_users(user1_token, user2_token)
        
        return MatchResponse(
            match_score=match_result['total_score'],
            match_strength=match_result['strength'].value,
            compatibility_reasons=match_result['reasons'],
            shared_artists=match_result['shared_items']['artists'],
            shared_genres=match_result['shared_items']['genres'],
            shared_tracks=match_result['shared_items']['tracks']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
