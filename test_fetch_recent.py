import copy
from unittest import result

import pytest

from fetch_recent import transform
from models import Track, Stream
from fetch_recent import save_cursor, load_cursor

mock_valid_item = {
    "played_at": "2026-05-29T14:34:38Z",
    "track": {
        "uri": "spotify:track:69kOkLUCkxIZYexIgSG8rq",
        "name": "Get Lucky",
        "album": {"name": "Random Access Memories"},
        "artists": [{"name": "Daft Punk"}, {"name": "Pharrell Williams"}],
    },
}


def test_valid_data_transform():
    expected_track = Track(
        uri="spotify:track:69kOkLUCkxIZYexIgSG8rq",
        artist="Daft Punk",
        name="Get Lucky",
        album="Random Access Memories",
    )
    expected_stream = Stream(
        ts="2026-05-29T14:34:38Z",
        ms_played=None,
        skipped=None,
        reason_start=None,
        reason_end=None,
        track_uri="spotify:track:69kOkLUCkxIZYexIgSG8rq",
    )
    result = transform(mock_valid_item)

    assert result == (expected_track, expected_stream)


def test_invalid_uri():
    invalid_track_uri_data = copy.deepcopy(mock_valid_item)

    del invalid_track_uri_data["track"]["uri"]

    with pytest.raises(ValueError):
        transform(invalid_track_uri_data)


def test_invalid_played_at():
    invalid_ts_data = copy.deepcopy(mock_valid_item)

    del invalid_ts_data["played_at"]

    with pytest.raises(ValueError):
        transform(invalid_ts_data)


def test_save_and_load_cursor(tmp_path):
    cursor_file = tmp_path / ".spotify_cursor"
    ts = "2026-05-08T17:26:43Z"
    save_cursor(ts, str(cursor_file))
    result = load_cursor(str(cursor_file))
    assert result == ts


def test_load_cursor_missing_file(tmp_path):
    cursor_file = tmp_path / ".spotify_cursor_none"
    result = load_cursor(str(cursor_file))
    assert result is None
