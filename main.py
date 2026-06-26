from pathlib import Path
from sqlite3 import Error

from db import create_connection, init_db, insert_itunes_playlist, insert_itunes_playlist_track, insert_itunes_track, insert_stream, insert_track
from pipeline.itunes import load_itunes_data, process_itunes_playlists, process_itunes_tracks
from pipeline.spotify import process_data

DATA_DIR = Path("./data")
ITUNES_XML = DATA_DIR / "iTunes Music Library.xml"


def main() -> None:
    conn = create_connection("listening_history.db")
    init_db(conn)

    # --- Spotify ---
    json_files = list(DATA_DIR.glob("*.json"))
    for file in json_files:
        records = process_data(file)
        for record in records:
            track, stream = record
            try:
                insert_track(conn, track)
                insert_stream(conn, stream)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting into table: {e}")

    # --- iTunes ---
    if ITUNES_XML.exists():
        library = load_itunes_data(ITUNES_XML)

        for itunes_track in process_itunes_tracks(library):
            try:
                insert_itunes_track(conn, itunes_track)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting iTunes track: {e}")

        playlists, playlist_tracks = process_itunes_playlists(library)

        for playlist in playlists:
            try:
                insert_itunes_playlist(conn, playlist)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting iTunes playlist: {e}")

        for playlist_track in playlist_tracks:
            try:
                insert_itunes_playlist_track(conn, playlist_track)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting iTunes playlist track: {e}")
    else:
        print(f"No iTunes library found at {ITUNES_XML}, skipping")
        
    conn.commit()


if __name__ == "__main__":
    main()
