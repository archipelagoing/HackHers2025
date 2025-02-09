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
async def get_matches(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")
            
        token = authorization.replace('Bearer ', '')
        sp = Spotify(auth=token)
        
        # Get current user's profile and data
        current_user = sp.current_user()
        current_user_id = current_user['id']
        print(f"Finding matches for user: {current_user['display_name']} ({current_user_id})")
        
        # Get current user's music data
        top_artists = sp.current_user_top_artists(limit=10)
        top_tracks = sp.current_user_top_tracks(limit=10)
        
        # Get audio features for top tracks
        track_ids = [track['id'] for track in top_tracks['items']]
        try:
            audio_features = sp.audio_features(track_ids)
            if audio_features and any(audio_features):
                avg_features = np.mean([[
                    f['danceability'],
                    f['energy'],
                    f['valence']
                ] for f in audio_features if f], axis=0)
            else:
                avg_features = np.array([0.5, 0.5, 0.5])  # Default values
        except Exception as e:
            print(f"Error getting audio features: {e}")
            avg_features = np.array([0.5, 0.5, 0.5])  # Default values
        
        # Prepare current user's data for matcher
        current_user_data = {
            'artists': [artist['name'] for artist in top_artists['items']],
            'tracks': [track['name'] for track in top_tracks['items']],
            'genres': list(set(genre for artist in top_artists['items'] for genre in artist['genres'])),
            'audio_features': np.array([avg_features])
        }
        
        # Get all users from database
        users_ref = db.collection('users')
        all_users = list(users_ref.stream())
        print(f"Found {len(all_users)} total users in database")
        
        # Initialize matcher
        matcher = FlirtifyMatcher()
        matches = []
        
        for user_doc in all_users:
            user_data = user_doc.to_dict()
            # Skip current user
            if user_data.get('spotify_id') == current_user_id:
                continue
            
            # Prepare other user's data
            other_user_data = {
                'artists': user_data.get('top_artists', []),
                'tracks': user_data.get('top_tracks', []),
                'genres': user_data.get('top_genres', []),
                'audio_features': np.array([[0.5, 0.5, 0.5]])  # Default if no audio features
            }
            
            # Calculate match
            match_result = matcher.calculate_match(current_user_data, other_user_data)
            match_score = match_result['score']
            
            print(f"\nMatching with {user_data.get('username')}:")
            print(f"Score: {match_score}")
            print(f"Shared artists: {match_result['shared_artists']}")
            print(f"Shared tracks: {match_result['shared_tracks']}")
            print(f"Shared genres: {match_result['shared_genres']}")
            
            if match_score > 20:  # Include matches with score above 20
                matches.append({
                    "user_id": user_data.get('spotify_id'),
                    "username": user_data.get('username'),
                    "profile_image": user_data.get('profile_image'),
                    "match_score": round(match_score, 1),
                    "shared_artists": match_result['shared_artists'],
                    "shared_tracks": match_result['shared_tracks'],
                    "shared_genres": match_result['shared_genres']
                })
        
        # Sort matches by score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        print(f"Found {len(matches)} matches above 20 points")
        
        return {"matches": matches}
        
    except Exception as e:
        print(f"Error getting matches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
