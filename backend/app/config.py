from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env into environment variables

CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("Claude API key not found in environment variables.")

