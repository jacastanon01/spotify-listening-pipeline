import json
from pathlib import Path
from typing import Any, Tuple
from models import Track, Stream


def load_data(path: Path) -> list[dict[str, Any]]:
    """
    Load the data from the JSON file and return it as a list of dictionaries.
    :param path: The file path to the JSON data file.
    :return: A list of dictionaries representing the data loaded from the JSON file.
    """
    with open(path, "r") as f:
        data: list[dict[str, Any]] = json.load(f)
    return data


def is_track(item: dict[str, Any]) -> bool:
    """
    Checks if the passed data is an episode or track object
    :param item: A dictionary representing a single data item loaded from the JSON file.
    :return: True if the item contains track information, False otherwise.
    """
    if item.get("spotify_track_uri"):
        return True
    return False


def convert_to_dataclasses(record: dict[str, Any]) -> Tuple[Track, Stream]:
    """
    Convert a dictionary record into Track and Stream dataclass instances.
    :param record: A dictionary representing a single data item loaded from the JSON file.
    :return: A tuple containing a Track dataclass instance and a Stream dataclass instance.
    """
    track = Track(
        uri=record["spotify_track_uri"],
        name=record["master_metadata_track_name"],
        artist=record["master_metadata_album_artist_name"],
        album=record["master_metadata_album_album_name"],
    )
    stream = Stream(
        ts=record["ts"],
        ms_played=record["ms_played"],
        skipped=record.get("skipped"),
        reason_start=record.get("reason_start"),
        reason_end=record.get("reason_end"),
        track_uri=record["spotify_track_uri"],
    )
    return track, stream


def process_data(path: Path) -> list[Tuple[Track, Stream]]:
    """
    Process the JSON data file and convert it into a list of Track and Stream dataclass instances.
    :param path: The file path to the JSON data file.
    :return: A list of tuples, where each tuple contains a Track dataclass instance and a Stream dataclass instance.
    """
    data = load_data(path)
    filtered_data = filter(is_track, data)
    processed_data = [convert_to_dataclasses(record) for record in filtered_data]
    return processed_data
