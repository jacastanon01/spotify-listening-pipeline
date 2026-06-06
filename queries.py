GET_YEARLY_PLAYS_MINUTES = """
SELECT 
    COUNT(*) as plays, 
    strftime('%Y', s.ts) as year, 
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s 
JOIN tracks t ON s.track_uri = t.uri
GROUP BY year
ORDER BY plays DESC;
"""