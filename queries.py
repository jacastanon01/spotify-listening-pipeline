GET_RAW_STREAMS_TIME = """
SELECT ts, ms_played, track_uri
FROM streams;
"""

GET_RAW_STREAMS_REASONS = """
SELECT reason_start, reason_end 
FROM streams;
"""

# how many itunes artists appear anywhere in Spotify tracks?
GET_FUZZY_ARTISTS_MATCH = """
SELECT COUNT(DISTINCT it.artist_normalized)
FROM itunes_tracks it
WHERE it.artist_normalized IN (
    SELECT DISTINCT lower(t.artist) FROM tracks t
);
"""

