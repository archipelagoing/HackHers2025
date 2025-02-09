from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass
from enum import Enum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database import db
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from firebase_admin import firestore

# Load environment variables
load_dotenv()

router = APIRouter()

# ============================
# 🎵 MATCH MODELS 🎵
# ============================

class MatchStrength(str, Enum):
    PERFECT = "PERFECT"    # 90-100%
    STRONG = "STRONG"      # 70-89%
    MODERATE = "MODERATE"  # 50-69%
    WEAK = "WEAK"         # 30-49%
    NO_MATCH = "NO_MATCH" # 0-29%

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

# ============================
# 🎵 SPOTIFY DATA FETCHING 🎵
# ============================

def get_spotify_client(user_id: str) -> spotipy.Spotify:
    """Get authenticated Spotify client for user"""
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_doc.to_dict()
    return spotipy.Spotify(auth=user_data.get('access_token'))

def get_user_top_artists(sp: spotipy.Spotify, limit=5) -> Tuple[List[str], List[str]]:
    """Fetch user's top artists and their genres"""
    results = sp.current_user_top_artists(limit=limit)
    artists = [item['name'] for item in results['items']]
    genres = list(set(genre for item in results['items'] for genre in item['genres']))
    return artists, genres

def get_user_top_tracks(sp: spotipy.Spotify, limit=5) -> List[str]:
    """Fetch user's top tracks"""
    results = sp.current_user_top_tracks(limit=limit)
    return [item['name'] for item in results['items']]

def get_audio_features(sp: spotipy.Spotify, track_ids: List[str]) -> np.ndarray:
    """Get audio features for tracks"""
    features = []
    for track_id in track_ids:
        audio_features = sp.audio_features([track_id])[0]
        if audio_features:
            features.append([
                audio_features['danceability'],
                audio_features['energy'],
                audio_features['valence']
            ])
    return np.array(features)

# ============================
# 🎵 MATCHING LOGIC 🎵
# ============================

class FlirtifyMatcher:
    def __init__(self):
        self.weights = {
            'artist_match': 30,
            'track_match': 20,
            'genre_match': 15,
            'audio_match': 35
        }
        
        self.thresholds = {
            'perfect': 90,
            'strong': 70,
            'moderate': 50,
            'weak': 30
        }

    def calculate_match(self, user1_data: Dict, user2_data: Dict) -> Dict:
        # Calculate individual scores
        artist_score = len(set(user1_data['artists']) & set(user2_data['artists'])) * self.weights['artist_match']
        track_score = len(set(user1_data['tracks']) & set(user2_data['tracks'])) * self.weights['track_match']
        genre_score = len(set(user1_data['genres']) & set(user2_data['genres'])) * self.weights['genre_match']
        
        # Audio features similarity
        if user1_data['audio_features'].size and user2_data['audio_features'].size:
            audio_sim = np.mean(cosine_similarity(user1_data['audio_features'], user2_data['audio_features']))
            audio_score = audio_sim * self.weights['audio_match']
        else:
            audio_score = 0
            
        total_score = artist_score + track_score + genre_score + audio_score
        
        # Determine match strength
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
            
        return {
            'score': total_score,
            'strength': strength,
            'shared_artists': list(set(user1_data['artists']) & set(user2_data['artists'])),
            'shared_tracks': list(set(user1_data['tracks']) & set(user2_data['tracks'])),
            'shared_genres': list(set(user1_data['genres']) & set(user2_data['genres']))
        }

# ============================
# 🎵 API ENDPOINTS 🎵
# ============================

@router.post("/match", response_model=MatchResponse)
async def match_users(request: MatchRequest):
    try:
        # Get Spotify clients for both users
        sp1 = get_spotify_client(request.user1_spotify_id)
        sp2 = get_spotify_client(request.user2_spotify_id)
        
        # Get music data for both users
        user1_artists, user1_genres = get_user_top_artists(sp1)
        user2_artists, user2_genres = get_user_top_artists(sp2)
        
        user1_tracks = get_user_top_tracks(sp1)
        user2_tracks = get_user_top_tracks(sp2)
        
        user1_data = {
            'artists': user1_artists,
            'genres': user1_genres,
            'tracks': user1_tracks,
            'audio_features': get_audio_features(sp1, [t['id'] for t in sp1.tracks(user1_tracks)['tracks']])
        }
        
        user2_data = {
            'artists': user2_artists,
            'genres': user2_genres,
            'tracks': user2_tracks,
            'audio_features': get_audio_features(sp2, [t['id'] for t in sp2.tracks(user2_tracks)['tracks']])
        }
        
        # Calculate match
        matcher = FlirtifyMatcher()
        match_result = matcher.calculate_match(user1_data, user2_data)
        
        # Generate compatibility reasons
        reasons = []
        if match_result['shared_artists']:
            reasons.append(f"You both love {', '.join(match_result['shared_artists'][:2])}")
        if match_result['shared_genres']:
            reasons.append(f"You share interests in {', '.join(match_result['shared_genres'][:2])}")
        if match_result['shared_tracks']:
            reasons.append(f"You both enjoy {', '.join(match_result['shared_tracks'][:2])}")
        
        # Store match result in Firebase
        db.collection('matches').add({
            'user1_id': request.user1_spotify_id,
            'user2_id': request.user2_spotify_id,
            'score': match_result['score'],
            'strength': match_result['strength'],
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        return MatchResponse(
            match_score=match_result['score'],
            match_strength=match_result['strength'],
            compatibility_reasons=reasons,
            shared_artists=match_result['shared_artists'],
            shared_genres=match_result['shared_genres'],
            shared_tracks=match_result['shared_tracks']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
