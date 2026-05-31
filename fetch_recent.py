import os
from typing import Any
import dotenv
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

from db import create_connection, insert_stream, insert_track
from models import Stream, Track
from pipeline import is_track

dotenv.load_dotenv()


def iso_to_unix_ms(ts: str) -> int:
    """
    :param ts: ISO timestamp to convert
    :return: unix timestamp in milliseconds
    """
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def init_spotipy() -> spotipy.Spotify:
    """
    Uses spotipy to initilize and return authorized spotify client to use
    """
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


def fetch_recent(
    sp: spotipy.Spotify, after: int | None = None
) -> dict[str, Any] | None:
    """
    uses spotipy web api to get 50 most recently played tracks
    :param sp: Authenticated spotipy client
    :return: JSON Response from Spotify API endpoint
    """
    return sp.current_user_recently_played(after=after)


def transform(item: dict[str, Any]) -> tuple[Track, Stream]:
    """
    Extracts data from repsonse, validates it and returns instantiated classes that organize into a format the DB will accept
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
        artist=(
            track_artists_list[0].get(
                "name", "Unknown Artist"
            )  # get name field from first artist listed in list
            if isinstance(
                track_artists_list[0], dict
            )  # verifies that first object is dictionary that contains name field
            else "Unknown Artist"
        ),
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


def save_cursor(ts: str, cursor_cache: str) -> None:
    """
    :param ts: ISO timestamp of listening event to log
    :param cursor_cache: location of file that has cursor log
    """
    with open(cursor_cache, "w") as f:
        f.write(ts)


def load_cursor(cursor_cache) -> str | None:
    """
    :param cursor_cache: location of file that has cursor log to read from
    :return: cursor saved from local file
    """
    try:
        with open(cursor_cache, "r") as f:
            cursor = f.read()
        return cursor
    except FileNotFoundError as e:
        print(f"Error loading from {cursor_cache}: {e}")
        return None


def main() -> None:
    sp = init_spotipy()
    cursor = load_cursor(".spotify_cursor")
    results = fetch_recent(sp, after=iso_to_unix_ms(cursor) if cursor else None)
    if results:
        items = results["items"]
        conn = create_connection("listening_history.db")
        for item in items:
            if is_track(item):
                track, stream = transform(item)
                insert_track(conn, track)
                insert_stream(conn, stream)
        conn.commit()
        if items:
            save_cursor(items[0]["played_at"], ".spotify_cursor")
        conn.close()
