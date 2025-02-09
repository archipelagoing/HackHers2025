from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass
from enum import Enum
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from ..database import db
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from firebase_admin import firestore
from spotipy import Spotify

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
    WEAK = "WEAK"         # 20-49%
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
            'artist_match': 35,
            'track_match': 20,
            'genre_match': 35,
            'audio_match': 10
        }
        
        self.thresholds = {
            'perfect': 80,
            'strong': 60,
            'moderate': 40,
            'weak': 20
        }

    def calculate_match(self, user1_data: Dict, user2_data: Dict) -> Dict:
        # Calculate individual scores with normalization
        shared_artists = set(user1_data['artists']) & set(user2_data['artists'])
        shared_tracks = set(user1_data['tracks']) & set(user2_data['tracks'])
        shared_genres = set(user1_data['genres']) & set(user2_data['genres'])
        
        # Normalize scores based on total possible matches
        artist_score = (len(shared_artists) / max(len(user1_data['artists']), 1)) * self.weights['artist_match']
        track_score = (len(shared_tracks) / max(len(user1_data['tracks']), 1)) * self.weights['track_match']
        genre_score = (len(shared_genres) / max(len(user1_data['genres']), 1)) * self.weights['genre_match']
        
        # Audio features similarity with more weight on danceability and energy
        if user1_data['audio_features'].size and user2_data['audio_features'].size:
            audio_sim = np.mean(cosine_similarity(user1_data['audio_features'], user2_data['audio_features']))
            audio_score = audio_sim * self.weights['audio_match']
        else:
            audio_score = 0
            
        total_score = artist_score + track_score + genre_score + audio_score
        
        # Scale score to 0-100
        total_score = min(100, total_score * 1.2)  # Boost scores slightly
        
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
            'shared_artists': list(shared_artists),
            'shared_tracks': list(shared_tracks),
            'shared_genres': list(shared_genres)
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

@router.get("/matches")
async def get_matches():
    """Get all matches for the current user"""
    try:
        # Get most recent user
        users_ref = db.collection('users')
        users = users_ref.order_by('last_login', direction='DESCENDING').limit(1).get()
        
        matches = []
        for user in users:
            current_user = user.to_dict()
            # Get all other users
            other_users = users_ref.where('spotify_id', '!=', current_user['spotify_id']).get()
            
            for other_user in other_users:
                other_user_data = other_user.to_dict()
                # Calculate match score based on shared music tastes
                match_score = calculate_match_score(current_user, other_user_data)
                
                matches.append({
                    "user_id": other_user.id,
                    "username": other_user_data.get('username'),
                    "profile_image": other_user_data.get('profile_image'),
                    "match_score": match_score,
                    "shared_artists": get_shared_artists(current_user, other_user_data),
                    "shared_genres": get_shared_genres(current_user, other_user_data),
                    "shared_tracks": get_shared_tracks(current_user, other_user_data)
                })
                
        return {"matches": sorted(matches, key=lambda x: x['match_score'], reverse=True)}
    except Exception as e:
        print(f"Error getting matches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_match_score(user1, user2):
    """Calculate match score between two users"""
    score = 0
    
    # Compare artists
    shared_artists = set(user1.get('top_artists', [])) & set(user2.get('top_artists', []))
    score += len(shared_artists) * 10
    
    # Compare genres
    shared_genres = set(user1.get('top_genres', [])) & set(user2.get('top_genres', []))
    score += len(shared_genres) * 5
    
    # Compare tracks
    shared_tracks = set(user1.get('top_tracks', [])) & set(user2.get('top_tracks', []))
    score += len(shared_tracks) * 8
    
    return min(score, 100)  # Cap at 100%

def get_shared_artists(user1, user2):
    return list(set(user1.get('top_artists', [])) & set(user2.get('top_artists', [])))

def get_shared_genres(user1, user2):
    return list(set(user1.get('top_genres', [])) & set(user2.get('top_genres', [])))

def get_shared_tracks(user1, user2):
    return list(set(user1.get('top_tracks', [])) & set(user2.get('top_tracks', [])))

@router.get("/debug/my-genres")
async def debug_my_genres(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")
            
        token = authorization.replace('Bearer ', '')
        sp = Spotify(auth=token)
        
        # Get current user's profile and genres
        current_user = sp.current_user()
        top_artists = sp.current_user_top_artists(limit=10)
        user_genres = set()
        for artist in top_artists['items']:
            user_genres.update(artist['genres'])
            
        return {
            "username": current_user['display_name'],
            "genres": list(user_genres)
        }
    except Exception as e:
        print(f"Error getting genres: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
