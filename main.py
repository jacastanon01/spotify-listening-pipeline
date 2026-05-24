import sqlite3
import json
from pathlib import Path
from typing import Dict, Any


WORKSPACE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = WORKSPACE_DIR / 'data'
DB_PATH: Path = WORKSPACE_DIR / 'spotify_warehouse.db'

def setup_database(cursor: sqlite3.Cursor) -> None:
    """
    Creates the two foundational tables for the Star Schema:
    1. media_catalog (The Item)
    2. listening_history (The Event)
    """
    
    # TODO: Write the CREATE TABLE statement for media_catalog
    # Columns needed: uri (TEXT PRIMARY KEY), media_type (TEXT), title (TEXT), creator (TEXT), album_name (TEXT)
    cursor.execute("""
        -- YOUR SQL HERE --
    """)

    # TODO: Write the CREATE TABLE statement for listening_history
    # Columns needed: stream_id (INTEGER PRIMARY KEY), media_uri (TEXT), played_at (TEXT), ms_played (INTEGER), skipped (BOOLEAN)
    # CRITICAL: Don't forget the UNIQUE constraint on (media_uri, played_at) to prevent duplicate streams!
    cursor.execute("""
        -- YOUR SQL HERE --
    """)

def process_spotify_files(cursor: sqlite3.Cursor, data_directory: Path) -> None:
    """
    Crawls the data directory, parses each JSON file, and inserts records into the database.
    """
    # .rglob() finds all files ending in .json anywhere inside the target folder
    for file_path in data_directory.rglob('*.json'):
        print(f"Processing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the JSON into a Python list of dictionaries
            # Type hint tells Pylance exactly what 'streams' is
            streams: list[Dict[str, Any]] = json.load(file)
            
            for stream in streams:
                # ---------------------------------------------------------
                # 1. EXTRACT: Pull values safely using .get()
                # ---------------------------------------------------------
                
                # TODO: Extract the timestamp, ms_played, and skipped status for the history table
                played_at = stream.get('...') 
                ms_played = stream.get('...')
                skipped = stream.get('...')
                
                # TODO: Extract the URI, track name, artist, and album for the catalog table
                uri = stream.get('...')
                title = stream.get('...')
                creator = stream.get('...')
                album_name = stream.get('...')
                
                # Check to handle podcasts vs songs, or skip local files missing a URI
                if not uri:
                    continue
                
                media_type = "Podcast" if "episode" in uri else "Song"

                # ---------------------------------------------------------
                # 2. LOAD: Insert into Database
                # ---------------------------------------------------------
                
                # TODO: Write the INSERT OR IGNORE statement for media_catalog
                # Pass your extracted Python variables into the SQL command using (?) placeholders
                cursor.execute("""
                    -- YOUR SQL HERE --
                """, (uri, media_type, title, creator, album_name))

                # TODO: Write the INSERT OR IGNORE statement for listening_history
                # Use (?) placeholders here as well
                cursor.execute("""
                    -- YOUR SQL HERE --
                """, (uri, played_at, ms_played, skipped))

def main() -> None:
    """
    Initializes the database connection, runs the pipeline, and commits changes.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Run the schema setup
        print("Setting up database schema...")
        setup_database(cursor)
        
        # Process the files
        print(f"Looking for JSON files in {DATA_DIR}...")
        process_spotify_files(cursor, DATA_DIR)
        
        # Save all changes to disk
        conn.commit()
        print("Pipeline execution complete. Data saved.")
        
    except Exception as e:
        # If anything crashes, undo any partial inserts to keep data clean
        conn.rollback()
        print(f"Pipeline failed: {e}")
        
    finally:
        # Always close the connection
        conn.close()

if __name__ == '__main__':
    main()