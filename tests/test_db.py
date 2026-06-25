import sqlite3
import pytest
from unittest.mock import patch, MagicMock

# Import the functions directly from your module
from db import (
    create_connection,
    init_db,
    insert_track,
    insert_stream,
    insert_itunes_track
)


# --- Fixtures ---

@pytest.fixture
def mem_db():
    """
    Provides a clean, in-memory SQLite database initialized with all tables.
    Closes the connection after the test completes.
    """
    conn = create_connection(":memory:")
    init_db(conn)
    yield conn
    conn.close()


# --- Tests for create_connection ---

def test_create_connection_success():
    """Test successful connection and PRAGMA execution."""
    conn = create_connection(":memory:")
    assert isinstance(conn, sqlite3.Connection)
    
    # Verify foreign keys are enabled
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    assert cursor.fetchone()[0] == 1
    conn.close()

@patch("sqlite3.connect")
def test_create_connection_failure(mock_connect):
    """Test that a sqlite3.Error raises a RuntimeError."""
    mock_connect.side_effect = sqlite3.Error("Connection denied")
    
    with pytest.raises(RuntimeError, match="Error connecting to database: Connection denied"):
        create_connection(":memory:")


# --- Tests for init_db ---

def test_init_db_success(mem_db):
    """Test that all specified tables are created."""
    cursor = mem_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    
    expected_tables = {
        "tracks", "streams", "itunes_tracks", 
        "track_matches", "itunes_playlists", "itunes_playlist_tracks"
    }
    assert expected_tables.issubset(tables)

def test_init_db_failure():
    """Test that a failure during initialization raises a RuntimeError."""
    mock_conn = MagicMock()
    # Trigger an error when the cursor tries to execute the statements
    mock_conn.cursor.return_value.execute.side_effect = sqlite3.Error("Syntax error")
    
    with pytest.raises(RuntimeError, match="Error initializing database: Syntax error"):
        init_db(mock_conn)


# --- Tests for insert_track ---

@patch("db.astuple")
def test_insert_track_success(mock_astuple, mem_db):
    """Test successful insertion of a Track."""
    # Mock astuple to return the tuple structure expected by the SQL query
    mock_astuple.return_value = ("spotify:track:123", "Test Song", "Test Artist", "Test Album")
    
    mock_track = MagicMock()
    insert_track(mem_db, mock_track)
    
    cursor = mem_db.cursor()
    cursor.execute("SELECT * FROM tracks")
    result = cursor.fetchone()
    
    assert result == ("spotify:track:123", "Test Song", "Test Artist", "Test Album")

@patch("db.astuple")
def test_insert_track_failure(mock_astuple):
    """Test error handling when inserting a Track fails."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.execute.side_effect = sqlite3.Error("Insert error")
    mock_astuple.return_value = ("mock_uri", "mock_name", "mock_artist", "mock_album")
    
    with pytest.raises(RuntimeError, match="Error inserting track: Insert error"):
        insert_track(mock_conn, MagicMock())


# --- Tests for insert_stream ---

@patch("db.astuple")
def test_insert_stream_success(mock_astuple, mem_db):
    """Test successful insertion of a Stream, adhering to Foreign Key constraints."""
    # 1. Insert a track first so the foreign key constraint is satisfied
    mem_db.execute(
        "INSERT INTO tracks (uri, name, artist, album) VALUES (?, ?, ?, ?)", 
        ("spotify:track:123", "Song", "Artist", "Album")
    )
    
    # 2. Mock astuple to return a stream tuple referencing the track URI
    mock_astuple.return_value = ("2023-10-01T12:00:00Z", 150000, False, "clickrow", "trackdone", "spotify:track:123")
    
    mock_stream = MagicMock()
    insert_stream(mem_db, mock_stream)
    
    cursor = mem_db.cursor()
    cursor.execute("SELECT ts, ms_played, skipped, reason_start, reason_end, track_uri FROM streams")
    result = cursor.fetchone()
    
    assert result == ("2023-10-01T12:00:00Z", 150000, 0, "clickrow", "trackdone", "spotify:track:123")

@patch("db.astuple")
def test_insert_stream_failure(mock_astuple):
    """Test error handling when inserting a Stream fails."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.execute.side_effect = sqlite3.Error("Stream insert error")
    mock_astuple.return_value = ("mock_ts", 0, False, "start", "end", "mock_uri")
    
    with pytest.raises(RuntimeError, match="Error inserting stream: Stream insert error"):
        insert_stream(mock_conn, MagicMock())


# --- Tests for insert_itunes_track ---

@patch("db.astuple")
def test_insert_itunes_track_success(mock_astuple, mem_db):
    """Test successful insertion of an ItunesTrack."""
    mock_astuple.return_value = (
        1, "iTunes Song", "iTunes Artist", "iTunes Album", 
        "Rock", 200000, 2010, 5, 1, 
        "2023-10-01T12:00:00Z", "2020-01-01T12:00:00Z", "itunes artist"
    )
    
    mock_itunes_track = MagicMock()
    insert_itunes_track(mem_db, mock_itunes_track)
    
    cursor = mem_db.cursor()
    cursor.execute("SELECT * FROM itunes_tracks")
    result = cursor.fetchone()
    
    assert result == (
        1, "iTunes Song", "iTunes Artist", "iTunes Album", 
        "Rock", 2010, 200000, 5, 1, 
        "2023-10-01T12:00:00Z", "2020-01-01T12:00:00Z", "itunes artist"
    )

@patch("db.astuple")
def test_insert_itunes_track_failure(mock_astuple):
    """Test error handling when inserting an iTunes track fails."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.execute.side_effect = sqlite3.Error("iTunes insert error")
    mock_astuple.return_value = (1, "name", "artist", "album", "genre", 0, 0, 0, 0, "last", "added", "norm")
    
    with pytest.raises(RuntimeError, match="Error inserting itunes track: iTunes insert error"):
        insert_itunes_track(mock_conn, MagicMock())