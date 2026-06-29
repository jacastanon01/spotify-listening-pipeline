import pytest
from models import ItunesTrack, TrackMatch
from populate_matches import build_artist_lookup, find_matches
from utils import normalize_track_name


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_itunes_track(track_id, name, artist, artist_normalized=None):
    """Helper to create ItunesTrack with minimal required fields."""
    return ItunesTrack(
        track_id=track_id,
        name=name,
        artist=artist,
        album=None,
        genre=None,
        year=None,
        duration_ms=180000,
        play_count=1,
        skip_count=0,
        last_played=None,
        date_added="2012-01-01T00:00:00",
        artist_normalized=artist_normalized or (artist.lower().strip() if artist else "unknown artist")
    )


# Spotify tracks as (uri, name, artist) tuples -- mirrors tracks table
SPOTIFY_TRACKS = [
    ("spotify:track:001", "Thirteen",       "Johnny Cash"),
    ("spotify:track:002", "Hurt",           "Nine Inch Nails"),
    ("spotify:track:003", "Hurt",           "Johnny Cash"),      # cover
    ("spotify:track:004", "Get It Together","Jurassic 5"),
    ("spotify:track:005", "Work It Out",    "Jurassic 5"),
    ("spotify:track:006", "Where Is My Mind","Pixies"),
]


# ---------------------------------------------------------------------------
# normalize_track_name
# ---------------------------------------------------------------------------

def test_normalize_track_name_lowercases():
    assert normalize_track_name("Get It Together") == "get it together"

def test_normalize_track_name_strips_whitespace():
    assert normalize_track_name("  Thirteen  ") == "thirteen"

def test_normalize_track_name_none_returns_empty_string():
    assert normalize_track_name(None) == ""

def test_normalize_track_name_strips_trailing_remastered():
    assert normalize_track_name("Thirteen (Remastered)") == normalize_track_name("Thirteen")

def test_normalize_track_name_strips_trailing_explicit():
    assert normalize_track_name("Thirteen [Explicit]") == normalize_track_name("Thirteen")

def test_normalize_track_name_strips_trailing_live():
    assert normalize_track_name("Get It Together (Live)") == normalize_track_name("Get It Together")

def test_normalize_track_name_does_not_strip_leading_paren():
    # (Don't Fear) The Reaper -- leading paren is part of the real title
    result = normalize_track_name("(Don't Fear) The Reaper")
    assert result.startswith("(")

def test_normalize_track_name_does_not_strip_leading_bracket():
    result = normalize_track_name("[en]strumental")
    assert result.startswith("[")


# ---------------------------------------------------------------------------
# build_artist_lookup
# ---------------------------------------------------------------------------

def test_build_artist_lookup_groups_by_normalized_artist():
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    assert "jurassic 5" in lookup
    assert len(lookup["jurassic 5"]) == 2

def test_build_artist_lookup_normalizes_artist_keys():
    # keys should be lowercased regardless of source casing
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    assert "johnny cash" in lookup
    assert "Johnny Cash" not in lookup

def test_build_artist_lookup_each_entry_has_uri_and_name():
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    entry = lookup["pixies"][0]
    assert entry[0] == "spotify:track:006"
    assert entry[1] == "Where Is My Mind"

def test_build_artist_lookup_empty_input_returns_empty():
    lookup = build_artist_lookup([])
    assert len(lookup) == 0


# ---------------------------------------------------------------------------
# find_matches
# ---------------------------------------------------------------------------

def test_find_matches_exact_artist_exact_track_is_exact_confidence():
    itunes = [make_itunes_track(1, "Thirteen", "Johnny Cash")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert len(matches) == 1
    assert matches[0].spotify_uri == "spotify:track:001"
    assert matches[0].match_confidence == "exact"

def test_find_matches_remastered_suffix_still_matches():
    # "Thirteen (Remastered)" should match "Thirteen" after normalization
    itunes = [make_itunes_track(1, "Thirteen (Remastered)", "Johnny Cash")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert len(matches) == 1
    assert matches[0].spotify_uri == "spotify:track:001"

def test_find_matches_cover_does_not_match_wrong_artist():
    # "Hurt" by Johnny Cash should NOT match "Hurt" by Nine Inch Nails
    itunes = [make_itunes_track(1, "Hurt", "Johnny Cash")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert len(matches) == 1
    # must match the Cash version, not NIN
    assert matches[0].spotify_uri == "spotify:track:003"

def test_find_matches_cover_nin_does_not_match_cash():
    itunes = [make_itunes_track(1, "Hurt", "Nine Inch Nails")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert len(matches) == 1
    assert matches[0].spotify_uri == "spotify:track:002"

def test_find_matches_no_match_returns_empty():
    itunes = [make_itunes_track(1, "Song Not In Spotify", "Artist Not In Spotify")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert matches == []

def test_find_matches_one_match_max_per_itunes_track():
    # Jurassic 5 has two Spotify tracks -- iTunes track should only match one
    itunes = [make_itunes_track(1, "Get It Together", "Jurassic 5")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    itunes_ids = [m.itunes_track_id for m in matches if m.itunes_track_id == 1]
    assert len(itunes_ids) == 1

def test_find_matches_fuzzy_artist_still_matches():
    # "Jurassic5" (no space) should fuzzy match "Jurassic 5"
    itunes = [make_itunes_track(1, "Get It Together", "Jurassic5",
                                artist_normalized="jurassic5")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert len(matches) == 1
    assert matches[0].match_confidence == "fuzzy"

def test_find_matches_different_track_same_artist_no_match():
    # track name that doesn't exist in Spotify for that artist
    itunes = [make_itunes_track(1, "Song That Does Not Exist", "Jurassic 5")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert matches == []

def test_find_matches_returns_track_match_instances():
    itunes = [make_itunes_track(1, "Thirteen", "Johnny Cash")]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert all(isinstance(m, TrackMatch) for m in matches)

def test_find_matches_multiple_itunes_tracks():
    itunes = [
        make_itunes_track(1, "Thirteen", "Johnny Cash"),
        make_itunes_track(2, "Get It Together", "Jurassic 5"),
        make_itunes_track(3, "Song Not In Spotify", "Nobody"),
    ]
    lookup = build_artist_lookup(SPOTIFY_TRACKS)
    matches = find_matches(itunes, lookup)
    assert len(matches) == 2
    matched_ids = {m.itunes_track_id for m in matches}
    assert matched_ids == {1, 2}