from pathlib import Path
from sqlite3 import Error

from db import create_connection, init_db, insert_itunes_playlist, insert_itunes_playlist_track, insert_itunes_track, insert_match, insert_stream, insert_track
from pipeline.itunes import load_itunes_data, process_itunes_playlists, process_itunes_tracks
from pipeline.spotify import load_spotify_data, process_spotify_data
from populate_matches import build_artist_lookup, find_matches, load_spotify_tracks

DATA_DIR = Path("./data")
ITUNES_XML = DATA_DIR / "iTunes Music Library.xml"


def main() -> None:
    conn = create_connection("listening_history.db")
    init_db(conn)
    print("Database initialized")

    # --- Spotify ---
    json_files = list(DATA_DIR.glob("*.json"))
    print(f"Found {len(json_files)} Spotify JSON file(s)")

    for file in json_files:
        print(f"  Processing {file.name}...")
        records = process_spotify_data(file)
        for record in records:
            track, stream = record
            try:
                insert_track(conn, track)
                insert_stream(conn, stream)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting into table: {e}")
        print(f"  ✓ {file.name} done")

    # --- iTunes ---
    if ITUNES_XML.exists():
        print(f"\nProcessing iTunes library...")
        library = load_itunes_data(ITUNES_XML)

        itunes_tracks = process_itunes_tracks(library)
        print(f"  Inserting {len(itunes_tracks)} tracks...")
        
        for itunes_track in itunes_tracks:
            try:
                if itunes_track is None:
                    print("No track to process from XML")
                else:
                    insert_itunes_track(conn, itunes_track)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting iTunes track: {e}")
        print(f"  ✓ iTunes tracks done")

        playlists, playlist_tracks = process_itunes_playlists(library)
        print(f"  Inserting {len(playlists)} playlists, {len(playlist_tracks)} memberships...")
        for playlist in playlists:
            try:
                insert_itunes_playlist(conn, playlist)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting iTunes playlist: {e}")

        for playlist_track in playlist_tracks:
            try:
                insert_itunes_playlist_track(conn, playlist_track)
                print(f"  ✓ Playlists done")
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting iTunes playlist track: {e}")
        print("\nRunning track matching...")

        spotify_tracks = load_spotify_tracks(conn)
        spotify_by_artist = build_artist_lookup(spotify_tracks)
        matches = find_matches(itunes_tracks, spotify_by_artist)
        for match in matches:
            try:
                insert_match(conn, match)
            except Error as e:
                conn.rollback()
                raise RuntimeError(f"Error inserting match: {e}")
        print("  ✓ Matching complete")
    else:
        print(f"\nNo iTunes library found at {ITUNES_XML}, skipping")


    conn.commit()
    print("\n✓ All data committed successfully")

    
if __name__ == "__main__":
    main()
