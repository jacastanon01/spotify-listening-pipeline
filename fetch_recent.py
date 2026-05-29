import os
import dotenv
import spotipy

from spotipy.oauth2 import SpotifyOAuth

dotenv.load_dotenv()


def init_spotipy() -> spotipy.Spotify:
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
            scope="user-read-recently-played",
            cache_path="./.spotify_cache",
        )
    )
    return sp
