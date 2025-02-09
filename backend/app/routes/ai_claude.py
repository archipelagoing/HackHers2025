# backend/app/routes/ai_claude.py

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

@router.post("/add-test-user")
def add_test_user(user_id: str):
    """
    Add a test user with sample music data to Firestore.
    """
    test_user_data = {
        "top_artists": ["Taylor Swift", "The Weeknd", "Drake", "Doja Cat", "Post Malone"],
        "audio_features": {
            "danceability": 0.8,
            "energy": 0.7,
            "valence": 0.6,
            "tempo": 120,
            "instrumentalness": 0.1
        }
    }
    
    db.collection("users").document(user_id).set(test_user_data)
    return {"message": f"Test user {user_id} created successfully", "data": test_user_data}
