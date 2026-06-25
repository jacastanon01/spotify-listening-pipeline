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

@dataclass
class ItunesTrack:
    track_id: int
    name: str
    artist: str | None
    album: str | None
    genre: str | None
    duration_ms: int
    year: int | None
    plays: int
    skips: int
    last_played: str | None
    date_added: str | None
    artist_normalized: str

@dataclass
class ItunesPlaylist:
    playlist_id: int
    name: str | None

@dataclass 
class ItunesPlaylistTrack:
    playlist_id: int
    itunes_track_id: int