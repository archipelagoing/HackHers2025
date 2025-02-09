from typing import List
from pydantic import BaseModel

# Add user model for type safety:
class User(BaseModel):
    spotify_id: str
    username: str
    access_token: str
    refresh_token: str
    top_artists: List[str]
    top_tracks: List[str]
    genres: List[str] 