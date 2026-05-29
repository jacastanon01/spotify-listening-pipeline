from dataclasses import dataclass


@dataclass
class Track:
    uri: str
    name: str
    artist: str
    album: str


@dataclass
class Stream:
    ts: str
    ms_played: int | None
    skipped: bool | None
    reason_start: str | None
    reason_end: str | None
    track_uri: str
