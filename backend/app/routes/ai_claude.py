import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from anthropic import Anthropic
from app.database import db

# Load environment variables
load_dotenv()

# Retrieve the Claude API key from environment variables
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("Claude API key not found in environment variables.")

# Initialize Anthropic client
anthropic = Anthropic(api_key=CLAUDE_API_KEY)

router = APIRouter()

def call_claude_api(prompt: str) -> str:
    """
    Calls the Claude API with a given prompt and returns the generated text.
    """
    try:
        message = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        print("Response:", message)  # Debug info
        return message.content[0].text
        
    except Exception as e:
        print(f"Error details: {str(e)}")  # Debug info
        raise HTTPException(
            status_code=500,
            detail=f"Claude API error: {str(e)}"
        )

@router.get("/test-claude")
def test_claude(prompt: str):
    """
    Endpoint to test Claude API by providing a prompt.
    """
    completion = call_claude_api(prompt)
    return {"completion": completion}


@router.get("/claude-personality-bio")
def generate_personality_bio(user_id: str):
    """
    Generate a music personality bio using Claude.
    """
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return {"error": "User not found"}

    user_data = user_doc.to_dict()
    top_artists = user_data.get("top_artists", [])
    audio_features = user_data.get("audio_features", {})

    prompt = f"""
    The user listens to {', '.join(top_artists)}. 
    Their audio features might be {audio_features}.
    Write a fun, detailed personality profile that connects these music tastes 
    to unique personality traits and style. 
    Give it a lively, friendly tone.
    """

    completion = call_claude_api(prompt)
    # Store in Firestore
    db.collection("users").document(user_id).set({"claude_personality_bio": completion}, merge=True)

    return {"personality_bio": completion}

# ==============================
# 🎼 AI-Curated "First Playlist for You Two"
# ==============================
@router.get("/claude-shared-playlist")
def generate_shared_playlist(user1_id: str, user2_id: str):
    """
    Generate an AI-curated playlist description for two users.
    """
    user1_doc = db.collection("users").document(user1_id).get()
    user2_doc = db.collection("users").document(user2_id).get()

    if not user1_doc.exists or not user2_doc.exists:
        return {"error": "One or both users not found"}

    user1_data = user1_doc.to_dict()
    user2_data = user2_doc.to_dict()

    common_genres = list(set(user1_data.get("top_genres", [])) & set(user2_data.get("top_genres", [])))

    prompt = f"""
    Alex and Jordan just matched! Their favorite genres are {', '.join(common_genres)}.
    Generate a **fun, engaging playlist description** that combines their musical vibes 
    in an exciting way. Keep it energetic and playful!
    """

    completion = call_claude_api(prompt)

    # Store playlist description in Firestore
    db.collection("shared_playlists").add({
        "user1_id": user1_id,
        "user2_id": user2_id,
        "playlist_description": completion
    })

    return {"playlist_description": completion}

# ==============================
# 🎶 AI-Generated "Perfect Match" Description
# ==============================
@router.get("/claude-match-description")
def generate_match_description(user1_id: str, user2_id: str):
    """
    Generate a fun and engaging match description based on shared music tastes.
    """
    user1_doc = db.collection("users").document(user1_id).get()
    user2_doc = db.collection("users").document(user2_id).get()

    if not user1_doc.exists or not user2_doc.exists:
        return {"error": "One or both users not found"}

    user1_data = user1_doc.to_dict()
    user2_data = user2_doc.to_dict()

    # Extract relevant data
    user1_artists = user1_data.get("top_artists", [])
    user2_artists = user2_data.get("top_artists", [])
    common_genres = list(set(user1_data.get("top_genres", [])) & set(user2_data.get("top_genres", [])))

    avg_energy = round((user1_data.get("energy", 0.5) + user2_data.get("energy", 0.5)) / 2, 2)
    avg_tempo = round((user1_data.get("tempo", 120) + user2_data.get("tempo", 120)) / 2, 2)

    prompt = f"""
    User 1 loves: {', '.join(user1_artists)}. 
    User 2 loves: {', '.join(user2_artists)}. 
    They share these common genres: {', '.join(common_genres)}. 
    Their songs have a similar energy level of {avg_energy} and tempo of {avg_tempo} BPM.

    Write a **fun, engaging description** of why these two users would make a perfect music match.
    Keep it lively, positive, and relatable.
    """

    completion = call_claude_api(prompt)

    # Store match description in Firestore
    db.collection("matches").add({
        "user1_id": user1_id,
        "user2_id": user2_id,
        "match_description": completion
    })

    return {"match_description": completion}
