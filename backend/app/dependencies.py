from spotipy.oauth2 import SpotifyOAuth
import os

def get_spotify_oauth():
    """Returns a SpotifyOAuth instance for dependency injection"""
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope="user-read-private user-read-email user-top-read playlist-read-private user-read-currently-playing user-read-playback-state user-read-recently-played"
    ) 