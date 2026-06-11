GET_RAW_STREAMS_TIME = """
SELECT ts, ms_played, track_uri
FROM streams;
"""

GET_RAW_STREAMS_REASONS = """
SELECT reason_start, reason_end 
FROM streams;
"""