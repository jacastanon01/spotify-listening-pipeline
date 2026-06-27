import sqlite3

from models import ItunesPlaylist, ItunesPlaylistTrack, ItunesTrack, Track, Stream
from dataclasses import astuple


def create_connection(db_file: str, check_same_thread: bool = True) -> sqlite3.Connection:
    """
    create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :param check_same_thread: Boolean that flags whether connection is being ued for data ingestion or data retrieval 
    :return: Connection object or None
    """
    try:
        # Even though the ingestion pipeline uses sequential inserts, if check_same_thread was always set to false,
        # there is a risk of the application changing states while the pipeline processes the data on the same connection.
        # Adding the extra argument distinguishes the purpose of the connection thread. Defaults to True for safer injection
        # but will be set to False when being used for the streamlit application
        conn = sqlite3.connect(db_file, check_same_thread=check_same_thread) 
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Error connecting to database: {e}")


def init_db(conn: sqlite3.Connection) -> None:
    """
    Create all tables in the database. Safe to run multiple times --
    IF NOT EXISTS prevents overwriting existing tables or data.
    :param conn: Connection object
    """

    statements = [
        """CREATE TABLE IF NOT EXISTS tracks (
            uri     TEXT PRIMARY KEY,
            name    TEXT NOT NULL,
            artist  TEXT NOT NULL,
            album   TEXT NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS streams (
            id           INTEGER PRIMARY KEY,
            ts           TEXT NOT NULL,
            ms_played    INTEGER,
            skipped      BOOLEAN,
            reason_start TEXT,
            reason_end   TEXT,
            track_uri    TEXT NOT NULL,
            FOREIGN KEY (track_uri) REFERENCES tracks (uri),
            UNIQUE(ts, track_uri)
        );""",
        """CREATE TABLE IF NOT EXISTS itunes_tracks (
            track_id          INTEGER PRIMARY KEY,
            name              TEXT NOT NULL,
            artist            TEXT,
            album             TEXT,
            genre             TEXT,
            year              INTEGER,
            duration_ms       INTEGER NOT NULL,
            play_count        INTEGER DEFAULT 0,
            skip_count        INTEGER DEFAULT 0,
            last_played       TEXT,
            date_added        TEXT,
            artist_normalized TEXT NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS track_matches (
            itunes_track_id  INTEGER NOT NULL,
            spotify_uri      TEXT NOT NULL,
            match_confidence TEXT DEFAULT 'fuzzy',
            PRIMARY KEY (itunes_track_id, spotify_uri),
            FOREIGN KEY (itunes_track_id) REFERENCES itunes_tracks (track_id),
            FOREIGN KEY (spotify_uri) REFERENCES tracks (uri)
        );""",
        """CREATE TABLE IF NOT EXISTS itunes_playlists (
            playlist_id INTEGER PRIMARY KEY,
            name        TEXT NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS itunes_playlist_tracks (
            playlist_id     INTEGER NOT NULL,
            itunes_track_id INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, itunes_track_id),
            FOREIGN KEY (playlist_id) REFERENCES itunes_playlists (playlist_id),
            FOREIGN KEY (itunes_track_id) REFERENCES itunes_tracks (track_id)
        );"""
    ]

    try:
        cursor = conn.cursor()
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Error initializing database: {e}")
    

def insert_track(conn: sqlite3.Connection, track: Track) -> None:
    """
    Insert a track into the tracks table
    :param conn: Connection object
    :param track: Track object
    """
    sql = """
    INSERT OR IGNORE INTO tracks(uri, name, artist, album)
    VALUES(?, ?, ?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, astuple(track))
    except sqlite3.Error as e:
        raise RuntimeError(f"Error inserting track: {e}")


def insert_stream(conn: sqlite3.Connection, stream: Stream) -> None:
    """
    Insert a stream into the streams table
    :param conn: Connection object
    :param stream: Stream object
    """
    sql = """
    INSERT OR IGNORE INTO streams(ts, ms_played, skipped, reason_start, reason_end, track_uri)
    VALUES(?, ?, ?, ?, ?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, astuple(stream))
    except sqlite3.Error as e:
        raise RuntimeError(f"Error inserting stream: {e}")

def insert_itunes_track(conn: sqlite3.Connection, itunes_track: ItunesTrack) -> None:
    """
    Insert a track into the itunes_tracks table
    :param conn: Connection object
    :param itunes_track: ItunesTrack dataclass object
    """
    sql = """
    INSERT OR IGNORE INTO itunes_tracks(track_id, name, artist, album, genre, duration_ms, year, play_count, skip_count, last_played, date_added, artist_normalized)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, astuple(itunes_track))
    except sqlite3.Error as e:
        raise RuntimeError(f"Error inserting itunes track: {e}")
    
def insert_itunes_playlist(conn: sqlite3.Connection, itunes_playlist: ItunesPlaylist) -> None:
    """
    Insert a playlist into the itunes_playlists table
    :param conn: Connection object
    :param itunes_playlist: ItunesPlaylist dataclass object
    """
    sql = """
    INSERT OR IGNORE INTO itunes_playlists(playlist_id, name)
    VALUES(?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, astuple(itunes_playlist))
    except sqlite3.Error as e:
        raise RuntimeError(f"Error inserting itunes playlist: {e}")
    
def insert_itunes_playlist_track(conn: sqlite3.Connection, playlist_track: ItunesPlaylistTrack) -> None:
    """
    Insert a playlist-track membership into the itunes_playlist_tracks table
    :param conn: Connection object
    :param playlist_track: ItunesPlaylistTrack dataclass object
    """
    sql = """
    INSERT OR IGNORE INTO itunes_playlist_tracks(playlist_id, itunes_track_id)
    VALUES(?, ?);
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, astuple(playlist_track))
    except sqlite3.Error as e:
        raise RuntimeError(f"Error inserting itunes playlist track: {e}")