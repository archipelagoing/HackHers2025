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

@router.post("/match")
async def match_users(request: MatchRequest):
    """Match two users based on their music preferences"""
    try:
        # Get user data from Firestore
        user1_doc = db.collection('users').document(request.user1_spotify_id).get()
        user2_doc = db.collection('users').document(request.user2_spotify_id).get()
        
        if not user1_doc.exists or not user2_doc.exists:
            raise HTTPException(status_code=404, detail="One or both users not found")
            
        user1_data = user1_doc.to_dict()
        user2_data = user2_doc.to_dict()
        
        # Prepare data for matcher
        matcher_data1 = {
            'artists': user1_data['top_artists'],
            'tracks': user1_data['top_tracks'],
            'genres': user1_data['top_genres'],
            'audio_features': np.array([[
                user1_data['audio_features']['danceability'],
                user1_data['audio_features']['energy'],
                user1_data['audio_features']['valence']
            ]])
        }
        
        matcher_data2 = {
            'artists': user2_data['top_artists'],
            'tracks': user2_data['top_tracks'],
            'genres': user2_data['top_genres'],
            'audio_features': np.array([[
                user2_data['audio_features']['danceability'],
                user2_data['audio_features']['energy'],
                user2_data['audio_features']['valence']
            ]])
        }
        
        # Calculate match using FlirtifyMatcher
        matcher = FlirtifyMatcher()
        match_result = matcher.calculate_match(matcher_data1, matcher_data2)
        
        # Generate compatibility reasons
        compatibility_reasons = [
            f"You share {len(match_result['shared_artists'])} favorite artists",
            f"You share {len(match_result['shared_tracks'])} favorite tracks",
            f"You have {len(match_result['shared_genres'])} music genres in common"
        ]
            
        return MatchResponse(
            match_score=match_result['score'],
            match_strength=match_result['strength'],
            compatibility_reasons=compatibility_reasons,
            shared_artists=match_result['shared_artists'],
            shared_genres=match_result['shared_genres'],
            shared_tracks=match_result['shared_tracks']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
