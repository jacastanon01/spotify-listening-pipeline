import os
from typing import Any
import dotenv
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timezone

from models import Stream, Track

dotenv.load_dotenv()


def iso_to_unix_ms(ts: str) -> int:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


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


def fetch_recent(sp: spotipy.Spotify, cursor: int) -> dict[str, Any] | None:
    """
    :param sp: Authenticated spotipy client
    :return: JSON Response from Spotify API
    """
    return sp.current_user_recently_played(after=cursor)


def transform(item: dict[str, Any]) -> tuple[Track, Stream]:
    """
    :param item: item from spotify most recently played API reponse
    :return: A tuple containing a Track dataclass instance and a Stream dataclass instance.
    """

    # Extract
    track_obj = item.get("track", {})
    track_uri = track_obj.get("uri")
    track_name = track_obj.get("name")
    track_album = track_obj.get("album", {})
    track_artists_list = track_obj.get("artists", [])
    album_name = track_album.get("name")
    played_at = item.get("played_at")

    # Validate
    if (
        not track_obj
        or not track_name
        or not track_uri
        or not album_name
        or not track_artists_list
        or not played_at
    ):
        raise ValueError("Missing critical track data")

    # Transform
    track = Track(
        uri=track_uri,
        name=track_name,
        artist=track_artists_list[0].get("name", "Unknown Artist"),
        album=album_name,
    )
    stream = Stream(
        ts=played_at,
        ms_played=None,
        skipped=None,
        reason_start=None,
        reason_end=None,
        track_uri=track_uri,
    )

    return track, stream


"""
def save_cursor(ts):
"""

"""
def load_cursor():
"""

"""
def main():
"""
