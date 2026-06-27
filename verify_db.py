import sqlite3

conn = sqlite3.connect("listening_history.db")
cursor = conn.cursor()

tables = [
    "tracks",
    "streams", 
    "itunes_tracks",
    "itunes_playlists",
    "itunes_playlist_tracks",
    "track_matches"
]

print("=== Row Counts ===")
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<30} {count:>8}")

print("\n=== Sample iTunes Track ===")
row = cursor.execute("""
    SELECT track_id, name, artist, genre, year, play_count, artist_normalized 
    FROM itunes_tracks 
    LIMIT 1
""").fetchone()
print(row)

print("\n=== Sample Playlist with Track Count ===")
rows = cursor.execute("""
    SELECT p.name, COUNT(pt.itunes_track_id) as track_count
    FROM itunes_playlists p
    JOIN itunes_playlist_tracks pt ON p.playlist_id = pt.playlist_id
    GROUP BY p.name
    ORDER BY track_count DESC
    LIMIT 5
""").fetchall()
for row in rows:
    print(f"  {row[0]:<30} {row[1]} tracks")

print("\n=== Data Integrity Checks ===")

# Check for orphaned playlist track references
orphaned = cursor.execute("""
    SELECT COUNT(*) FROM itunes_playlist_tracks pt
    LEFT JOIN itunes_tracks t ON pt.itunes_track_id = t.track_id
    WHERE t.track_id IS NULL
""").fetchone()[0]
print(f"  Orphaned playlist-track references: {orphaned}")

# Check artist_normalized is never NULL
null_normalized = cursor.execute("""
    SELECT COUNT(*) FROM itunes_tracks 
    WHERE artist_normalized IS NULL
""").fetchone()[0]
print(f"  iTunes tracks with NULL artist_normalized: {null_normalized}")

# Check streams unique constraint is holding
total_streams = cursor.execute("SELECT COUNT(*) FROM streams").fetchone()[0]
unique_streams = cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT DISTINCT ts, track_uri FROM streams
    )
""").fetchone()[0]
print(f"  Total streams: {total_streams}, Unique (ts, track_uri): {unique_streams}")

# Minimum row count assertions -- fail loudly if something went wrong
assert total_streams > 80000, f"Stream count suspiciously low: {total_streams}"
assert cursor.execute("SELECT COUNT(*) FROM itunes_tracks").fetchone()[0] == 5582, "iTunes track count mismatch"
assert cursor.execute("SELECT COUNT(*) FROM itunes_playlists").fetchone()[0] == 42, "Playlist count mismatch"
print("\n  ✓ All assertions passed")

conn.close()