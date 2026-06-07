GET_YEARLY_PLAYS_MINUTES = """
SELECT 
    COUNT(*) as plays, 
    strftime('%Y', s.ts) as year, 
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s 
JOIN tracks t ON s.track_uri = t.uri
WHERE CAST(strftime('%Y', s.ts) AS INTEGER) BETWEEN ? AND ?
GROUP BY year
ORDER BY year ASC;
"""

GET_YEARLY_TOP_ARTISTS = """
SELECT t.artist, 
    strftime('%Y', s.ts) as year,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s 
JOIN tracks t ON s.track_uri = t.uri
WHERE CAST(strftime('%Y', s.ts) AS INTEGER) BETWEEN ? AND ?
GROUP BY t.artist
ORDER BY minutes_played DESC
LIMIT 15;
"""

GET_YEARLY_TOP_TRACKS = """
SELECT t.artist, t.name,
    strftime('%Y', s.ts) as year,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s 
JOIN tracks t ON s.track_uri = t.uri
WHERE CAST(strftime('%Y', s.ts) AS INTEGER) BETWEEN ? AND ?
GROUP BY t.uri
ORDER BY minutes_played DESC
LIMIT 15;
"""

GET_TIME_OF_DAY_LISTENS = """
SELECT 
    strftime('%H', s.ts) as hour, 
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
GROUP BY hour 
ORDER BY hour ASC;
"""