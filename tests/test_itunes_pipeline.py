import plistlib
from datetime import datetime
from pathlib import Path

import pytest

from models import ItunesPlaylist, ItunesPlaylistTrack, ItunesTrack
from pipeline.itunes import (
    convert_to_itunes_track,
    convert_to_playlist,
    is_system_playlist,
    load_itunes_data,
    process_itunes_playlists,
    process_itunes_tracks,
)


# ---------------------------------------------------------------------------
# Fixtures -- raw dicts that mirror what plistlib actually returns
# plistlib gives you datetime objects for date fields, not strings
# these match the real structure you saw in the pprint output
# ---------------------------------------------------------------------------

FULL_TRACK = {
    "Track ID": 3180,
    "Name": "Get It Together",
    "Artist": "Jurassic 5",
    "Album": "Feedback",
    "Genre": "Hip Hop/Rap",
    "Year": 2006,
    "Total Time": 213026,
    "Play Count": 4,
    "Skip Count": 1,
    "Play Date UTC": datetime(2015, 4, 15, 6, 41, 56),
    "Date Added": datetime(2010, 12, 12, 21, 17, 39),
}

# Track with Stop Time set -- duration_ms should use Stop Time, not Total Time
TRACK_WITH_STOP_TIME = {
    **FULL_TRACK,
    "Track ID": 3181,
    "Stop Time": 193026,
    "Total Time": 213026,
}

# Track with no Artist key -- normalize_artist should return "unknown artist"
NO_ARTIST_TRACK = {
    **FULL_TRACK,
    "Track ID": 3182,
    "Artist": None,
}

# Track that was never played -- Play Count and Play Date UTC keys are absent entirely
NEVER_PLAYED_TRACK = {
    "Track ID": 3183,
    "Name": "Thirteen",
    "Artist": "Johnny Cash",
    "Album": "American Recordings",
    "Genre": "Country",
    "Year": 1994,
    "Total Time": 149733,
    "Date Added": datetime(2010, 12, 12, 21, 17, 39),
    # no Play Count key
    # no Skip Count key
    # no Play Date UTC key
}

# Minimal track -- only required fields present
MINIMAL_TRACK = {
    "Track ID": 3184,
    "Name": "Legalize It",
    "Total Time": 279666,
    "Date Added": datetime(2010, 12, 12, 21, 17, 39),
}

# Sample library dict -- mirrors the top-level structure plistlib returns
SAMPLE_LIBRARY = {
    "Tracks": {
        "3180": FULL_TRACK,
        "3182": NO_ARTIST_TRACK,
        "3183": NEVER_PLAYED_TRACK,
    },
    "Playlists": [
        # system playlist -- should be filtered out (Master flag)
        {
            "Playlist ID": 1,
            "Name": "####!####",
            "Master": True,
            "Playlist Items": [{"Track ID": 3180}],
        },
        # system playlist -- should be filtered out (known system name)
        {
            "Playlist ID": 2,
            "Name": "Music",
            "Playlist Items": [{"Track ID": 3180}, {"Track ID": 3182}],
        },
        # system playlist -- should be filtered out (Visible = False)
        {
            "Playlist ID": 3,
            "Name": "Podcasts",
            "Visible": False,
            "Playlist Items": [],
        },
        # user playlist -- should be kept
        {
            "Playlist ID": 4,
            "Name": "beats",
            "Playlist Items": [{"Track ID": 3180}, {"Track ID": 3183}],
        },
        # user playlist with no items -- edge case, should still be kept
        {
            "Playlist ID": 5,
            "Name": "Autumn",
        },
    ],
}


# ---------------------------------------------------------------------------
# load_itunes_data
# uses pytest's tmp_path fixture to create a real plist file on disk
# this verifies the function opens in binary mode without mocking internals
# ---------------------------------------------------------------------------

def test_load_itunes_data_returns_dict(tmp_path):
    # write a minimal valid plist to a temp file
    test_data = {"Tracks": {}, "Playlists": []}
    test_file = tmp_path / "test_library.xml"
    with open(test_file, "wb") as f:
        plistlib.dump(test_data, f, fmt=plistlib.FMT_XML)

    result = load_itunes_data(test_file)
    assert result == test_data


def test_load_itunes_data_raises_on_missing_file(tmp_path):
    # passing a path that does not exist should raise an error, not return None
    missing = tmp_path / "nonexistent.xml"
    with pytest.raises(FileNotFoundError):
        load_itunes_data(missing)


# ---------------------------------------------------------------------------
# convert_to_itunes_track
# ---------------------------------------------------------------------------

def test_convert_full_track_maps_all_fields():
    result = convert_to_itunes_track(FULL_TRACK)
    assert isinstance(result, ItunesTrack)
    assert result.track_id == 3180
    assert result.name == "Get It Together"
    assert result.artist == "Jurassic 5"
    assert result.album == "Feedback"
    assert result.genre == "Hip Hop/Rap"
    assert result.year == 2006
    assert result.play_count == 4
    assert result.skip_count == 1


def test_convert_track_uses_stop_time_over_total_time():
    # when Stop Time is present it represents the actual playback endpoint
    # duration_ms should reflect this, not the full track length
    result = convert_to_itunes_track(TRACK_WITH_STOP_TIME)
    assert result.duration_ms == 193026


def test_convert_track_falls_back_to_total_time_when_no_stop_time():
    result = convert_to_itunes_track(FULL_TRACK)
    assert result.duration_ms == 213026


def test_convert_track_datetime_fields_converted_to_iso_string():
    result = convert_to_itunes_track(FULL_TRACK)
    # plistlib gives datetime objects -- the dataclass should store ISO strings
    assert isinstance(result.last_played, str)
    assert result.last_played == "2015-04-15T06:41:56"
    assert isinstance(result.date_added, str)
    assert result.date_added == "2010-12-12T21:17:39"


def test_convert_track_never_played_has_none_last_played():
    # Play Date UTC key is absent entirely on unplayed tracks
    # result should be None, not an error
    result = convert_to_itunes_track(NEVER_PLAYED_TRACK)
    assert result.last_played is None


def test_convert_track_never_played_has_zero_play_count():
    # Play Count key is absent on unplayed tracks -- should default to 0
    result = convert_to_itunes_track(NEVER_PLAYED_TRACK)
    assert result.play_count == 0


def test_convert_track_never_skipped_has_zero_skip_count():
    # Skip Count key is absent when never skipped -- should default to 0
    result = convert_to_itunes_track(NEVER_PLAYED_TRACK)
    assert result.skip_count == 0


def test_convert_track_no_artist_sets_normalized_to_unknown():
    result = convert_to_itunes_track(NO_ARTIST_TRACK)
    assert result.artist is None
    assert result.artist_normalized == "unknown artist"


def test_convert_track_normalizes_artist_name():
    # artist_normalized should be lowercase with punctuation stripped
    messy = {**FULL_TRACK, "Artist": "KiD CuDi!"}
    result = convert_to_itunes_track(messy)
    assert result.artist_normalized == "kid cudi"


def test_convert_track_nullable_fields_can_be_none():
    # minimal track with only required fields should not raise
    result = convert_to_itunes_track(MINIMAL_TRACK)
    assert result.genre is None
    assert result.year is None
    assert result.album is None


# ---------------------------------------------------------------------------
# process_itunes_tracks
# ---------------------------------------------------------------------------

def test_process_itunes_tracks_returns_correct_count():
    result = process_itunes_tracks(SAMPLE_LIBRARY)
    assert len(result) == 3


def test_process_itunes_tracks_returns_list_of_itunes_track():
    result = process_itunes_tracks(SAMPLE_LIBRARY)
    assert all(isinstance(t, ItunesTrack) for t in result)


def test_process_itunes_tracks_empty_library_returns_empty_list():
    result = process_itunes_tracks({"Tracks": {}})
    assert result == []


# ---------------------------------------------------------------------------
# is_system_playlist
# ---------------------------------------------------------------------------

def test_master_playlist_is_system():
    playlist = {"Name": "####!####", "Master": True}
    assert is_system_playlist(playlist) is True


def test_hidden_playlist_is_system():
    # Visible = False means system-hidden
    playlist = {"Name": "Podcasts", "Visible": False}
    assert is_system_playlist(playlist) is True


def test_known_system_name_is_system():
    playlist = {"Name": "Music"}
    assert is_system_playlist(playlist) is True


def test_user_playlist_is_not_system():
    playlist = {"Name": "beats"}
    assert is_system_playlist(playlist) is False


def test_visible_true_is_not_system():
    # Visible = True means the playlist is visible -- should NOT be filtered
    playlist = {"Name": "beats", "Visible": True}
    assert is_system_playlist(playlist) is False


def test_visible_key_absent_is_not_system():
    # absence of Visible key means visible -- should NOT be filtered
    # this distinguishes None from False
    playlist = {"Name": "chill hip hop"}
    assert is_system_playlist(playlist) is False


# ---------------------------------------------------------------------------
# convert_to_playlist
# ---------------------------------------------------------------------------

def test_convert_to_playlist_returns_correct_playlist():
    raw = {
        "Playlist ID": 4,
        "Name": "beats",
        "Playlist Items": [{"Track ID": 3180}, {"Track ID": 3183}],
    }
    playlist, _ = convert_to_playlist(raw)
    assert isinstance(playlist, ItunesPlaylist)
    assert playlist.playlist_id == 4
    assert playlist.name == "beats"


def test_convert_to_playlist_returns_correct_track_memberships():
    raw = {
        "Playlist ID": 4,
        "Name": "beats",
        "Playlist Items": [{"Track ID": 3180}, {"Track ID": 3183}],
    }
    _, memberships = convert_to_playlist(raw)
    assert len(memberships) == 2
    assert all(isinstance(m, ItunesPlaylistTrack) for m in memberships)
    assert all(m.playlist_id == 4 for m in memberships)
    track_ids = {m.itunes_track_id for m in memberships}
    assert track_ids == {3180, 3183}


def test_convert_to_playlist_empty_items_returns_empty_membership_list():
    # playlists with no Playlist Items key should not raise
    raw = {"Playlist ID": 5, "Name": "Autumn"}
    playlist, memberships = convert_to_playlist(raw)
    assert playlist.name == "Autumn"
    assert memberships == []


# ---------------------------------------------------------------------------
# process_itunes_playlists
# ---------------------------------------------------------------------------

def test_process_itunes_playlists_filters_system_playlists():
    # SAMPLE_LIBRARY has 3 system playlists and 2 user playlists
    playlists, _ = process_itunes_playlists(SAMPLE_LIBRARY)
    assert len(playlists) == 2
    names = {pl.name for pl in playlists}
    assert names == {"beats", "Autumn"}


def test_process_itunes_playlists_returns_flat_membership_list():
    # beats has 2 items, Autumn has 0 -- total should be 2
    _, memberships = process_itunes_playlists(SAMPLE_LIBRARY)
    assert len(memberships) == 2
    assert all(isinstance(m, ItunesPlaylistTrack) for m in memberships)


def test_process_itunes_playlists_empty_library_returns_empty_lists():
    playlists, memberships = process_itunes_playlists({"Playlists": []})
    assert playlists == []
    assert memberships == []