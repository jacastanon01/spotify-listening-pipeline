import sqlite3


def create_connection(db_file: str) -> sqlite3.Connection:
    """create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(f"Error connecting to database: {e}")


def init_db(conn: sqlite3.Connection) -> None:
    """create tables in the database
    :param conn: Connection object
    """
    create_tracks_table = """
    CREATE TABLE IF NOT EXISTS tracks (
        uri TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        artist TEXT NOT NULL,
        album TEXT NOT NULL
    );"""

    create_streams_table = """
    CREATE TABLE IF NOT EXISTS streams (
        id INTEGER PRIMARY KEY,
        ts TEXT,
        ms_played INTEGER NOT NULL,
        skipped BOOLEAN,
        reason_start TEXT,
        reason_end TEXT,
        track_uri TEXT NOT NULL,
        FOREIGN KEY (track_uri) REFERENCES tracks (uri)
    );"""

    try:
        cursor = conn.cursor()
        cursor.execute(create_tracks_table)
        cursor.execute(create_streams_table)
        conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Error initializing database: {e}")
