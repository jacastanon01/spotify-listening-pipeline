from models import Stream, Track
from pipeline import convert_to_dataclasses, is_track
from typing import Any

import pytest

mock_record: dict[str, Any] = {
    "ts": "2026-05-08T17:26:43Z",
    "platform": "ios",
    "ms_played": 870,
    "conn_country": "US",
    "ip_addr": "2605:a601:afdc:c900:cca2:9a0a:7f5a:e273",
    "master_metadata_track_name": "Free Mind",
    "master_metadata_album_artist_name": "Tems",
    "master_metadata_album_album_name": "For Broken Ears",
    "spotify_track_uri": "spotify:track:2mzM4Y0Rnx2BDZqRnhQ5Q6",
    "episode_name": None,
    "episode_show_name": None,
    "spotify_episode_uri": None,
    "audiobook_title": None,
    "audiobook_uri": None,
    "audiobook_chapter_uri": None,
    "audiobook_chapter_title": None,
    "reason_start": "unknown",
    "reason_end": "endplay",
    "shuffle": False,
    "skipped": True,
    "offline": False,
    "offline_timestamp": 1778261202,
    "incognito_mode": False,
}


def test_is_track():
    result = is_track(mock_record)
    assert result


def test_is_not_track():
    episode_record: dict[str, Any] = {
        **mock_record,
        "spotify_track_uri": None,
    }
    result = is_track(episode_record)
    assert not result


def test_convert_to_dataclasses():
    expected_track = Track(
        uri="spotify:track:2mzM4Y0Rnx2BDZqRnhQ5Q6",
        name="Free Mind",
        artist="Tems",
        album="For Broken Ears",
    )
    expected_stream = Stream(
        ts="2026-05-08T17:26:43Z",
        ms_played=870,
        skipped=True,
        reason_start="unknown",
        reason_end="endplay",
        track_uri="spotify:track:2mzM4Y0Rnx2BDZqRnhQ5Q6",
    )
    result = convert_to_dataclasses(mock_record)
    assert result == (expected_track, expected_stream)


def test_missing_track_name_raises():
    invalid_track_name: dict[str, Any] = {
        **mock_record,
        "master_metadata_track_name": None,
    }
    with pytest.raises(ValueError):
        convert_to_dataclasses(invalid_track_name)


def test_missing_ms_played_raises():
    invalid_ms_played: dict[str, Any] = {
        **mock_record,
        "ms_played": None,
    }
    with pytest.raises(ValueError):
        convert_to_dataclasses(invalid_ms_played)
