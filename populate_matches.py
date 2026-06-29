from collections import defaultdict
from rapidfuzz import fuzz

from models import ItunesTrack, TrackMatch
from utils import normalize_track_name


ARTIST_THRESHOLD = 90
TRACK_THRESHOLD = 85


def load_spotify_tracks(conn) -> list[tuple]:
    """
    Load all tracks from the Spotify tracks table.
    :param conn: Connection object
    :return: List of (uri, name, artist) tuples
    """
    return conn.execute("SELECT uri, name, artist FROM tracks").fetchall()


def build_artist_lookup(spotify_tracks: list[tuple]) -> dict:
    """
    Group Spotify tracks by normalized artist name.
    Avoids comparing every iTunes track against all 26,602 Spotify tracks.
    Instead each iTunes track only compares against tracks by the same artist.
    :param spotify_tracks: List of (uri, name, artist) tuples from tracks table
    :return: Dict mapping normalized artist name to list of (uri, name) tuples
    """
    lookup = defaultdict(list)
    for uri, name, artist in spotify_tracks:
        key = artist.lower().strip()
        lookup[key].append((uri, name))
    return lookup


def find_matches(
    itunes_tracks: list[ItunesTrack | None],
    spotify_by_artist: dict,
) -> list[TrackMatch]:
    """
    Two-pass matching strategy.

    Pass 1 -- exact artist: check if artist_normalized is a direct key in
    the lookup dict. If found, compare track names with fuzz.ratio.
    A track score of 100 gets confidence 'exact'. Above threshold gets 'fuzzy'.

    Pass 2 -- fuzzy artist: for tracks with no exact artist match, compare
    artist_normalized against every Spotify artist key with fuzz.ratio.
    If an artist scores above ARTIST_THRESHOLD, compare track names.
    All matches from this pass get confidence 'fuzzy'.

    Both artist AND track must meet threshold. One match max per iTunes track.
    This prevents covers from creating false matches -- "Hurt" by NIN and
    "Hurt" by Johnny Cash both normalize to "hurt" but their artists won't
    match each other above threshold.

    :param itunes_tracks: List of ItunesTrack dataclasses already in memory
    :param spotify_by_artist: Lookup dict from build_artist_lookup
    :return: List of TrackMatch dataclasses ready for insertion
    """
    matches = []
    spotify_artist_keys = list(spotify_by_artist.keys())

    for itrack in itunes_tracks:
        itunes_name = normalize_track_name(itrack.name)
        matched = False

        # pass 1: exact artist match
        if itrack.artist_normalized in spotify_by_artist:
            candidates = spotify_by_artist[itrack.artist_normalized]
            for uri, spotify_name in candidates:
                track_score = fuzz.ratio(itunes_name, normalize_track_name(spotify_name))
                if track_score >= TRACK_THRESHOLD:
                    confidence = 'exact' if track_score == 100 else 'fuzzy'
                    matches.append(TrackMatch(
                        itunes_track_id=itrack.track_id,
                        spotify_uri=uri,
                        match_confidence=confidence
                    ))
                    matched = True
                    break

        if matched:
            continue

        # pass 2: fuzzy artist match on remainder
        for spotify_artist in spotify_artist_keys:
            artist_score = fuzz.ratio(itrack.artist_normalized, spotify_artist)
            if artist_score >= ARTIST_THRESHOLD:
                candidates = spotify_by_artist[spotify_artist]
                for uri, spotify_name in candidates:
                    track_score = fuzz.ratio(
                        itunes_name,
                        normalize_track_name(spotify_name)
                    )
                    if track_score >= TRACK_THRESHOLD:
                        matches.append(TrackMatch(
                            itunes_track_id=itrack.track_id,
                            spotify_uri=uri,
                            match_confidence='fuzzy'
                        ))
                        matched = True
                        break
            if matched:
                break

    print(f"  Found {len(matches)} matches from {len(itunes_tracks)} iTunes tracks")
    return matches