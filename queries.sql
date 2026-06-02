-- ============================================================
-- Spotify Listening History — Analysis Queries
-- Run against listening_history.db
-- Tip: use `.mode markdown` and `.headers on` in the SQLite
-- shell to output results as markdown tables
-- ============================================================


-- Listening volume by year with depth vs breadth metric
-- plays_per_artist reveals whether listening was broad exploration
-- or focused deep dives into fewer artists
SELECT strftime('%Y', s.ts) as year,
       COUNT(DISTINCT t.artist) as unique_artists,
       COUNT(*) as total_plays,
       ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT t.artist), 1) as plays_per_artist
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
GROUP BY year
ORDER BY plays_per_artist DESC;

-- How many streaming events were created each year
SELECT strftime('%Y', ts) as year, COUNT(*) as plays 
FROM streams 
JOIN tracks t ON streams.track_uri = t.uri 
WHERE t.artist != 'Sleepy Dogs' -- Excluding calming music I played for my dog at the time, which dominated 2022
GROUP BY year ORDER BY plays desc;


-- Top artists from the first peak listening period (2018-2020)
SELECT t.artist, 
    COUNT(*) as plays,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2018', '2019', '2020')
GROUP BY t.artist
ORDER BY minutes_played DESC
LIMIT 15;


-- Top tracks from the first peak listening period (2018-2020)
SELECT t.name, t.artist, 
    COUNT(*) as plays,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2018', '2019', '2020')
GROUP BY t.name, t.artist
ORDER BY minutes_played DESC
LIMIT 15;


-- Top artists from the recent listening period (2024-2025)
SELECT t.artist, 
    COUNT(*) as plays,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2024', '2025')
GROUP BY t.artist
ORDER BY minutes_played DESC
LIMIT 15;


-- Top tracks from the recent listening period by stream event (2024-2025)
SELECT t.name, t.artist, 
    COUNT(*) as plays,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2024', '2025')
GROUP BY t.name, t.artist
ORDER BY minutes_played DESC
LIMIT 15;

-- Top tracks by minutes played (2024-2025)
SELECT t.name, t.artist, 
       COUNT(*) as plays,
       ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2024', '2025')
AND s.ms_played IS NOT NULL
GROUP BY t.name, t.artist
ORDER BY minutes_played DESC
LIMIT 15;


-- Listening volume by hour of day (24 hour format)
-- Reveals time of day patterns across the full dataset
SELECT strftime('%H', ts) as hour, COUNT(*) as plays
FROM streams
GROUP BY hour
ORDER BY plays DESC;


-- How tracks entered the listening queue
-- clickrow = actively chosen, fwdbtn = skipped forward to,
-- trackdone = natural autoplay, backbtn = went back
-- Reveals whether listening is active and intentional or passive
SELECT reason_start, COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM streams
GROUP BY reason_start
ORDER BY count DESC;


-- Tracks played more than 10 times with a skip rate below 20%
-- These are genuine favorites, songs returned to repeatedly
-- that almost always get listened through
-- Note: skip data only reliable from 2023 onward
SELECT ROUND(AVG(s.skipped) * 100, 1) as skip_rate_pct,
    t.name, t.artist, COUNT(*) as plays,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE s.skipped IS NOT NULL
GROUP BY t.name, t.artist
HAVING minutes_played >= 99 AND AVG(s.skipped) < 0.2
ORDER BY skip_rate_pct
LIMIT 15;

-- Tracks played more than 10 times with a skip rate below 20%
-- These are genuine favorites, songs returned to repeatedly
-- that almost always get listened through
-- Only include years after 2022 to adjust for unreliable skip data
SELECT ROUND(AVG(s.skipped) * 100, 1) as skip_rate_pct,
    t.name, t.artist, COUNT(*) as plays,
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE s.skipped IS NOT NULL
AND strftime('%Y', s.ts) in ('2023', '2024', '2025', '2026')
GROUP BY t.name, t.artist
HAVING minutes_played >= 100 AND AVG(s.skipped) < 0.4
ORDER BY skip_rate_pct
LIMIT 15;

-- Tracks with a total listening time of at least 30 minutes 
-- that were chosen deliberately and played to completion
SELECT t.name, t.artist, 
    ROUND(SUM(s.ms_played) / 60000.0, 1) as minutes_played
FROM streams s
JOIN tracks t ON s.track_uri = t.uri 
WHERE s.reason_start = 'clickrow'
AND s.reason_end = 'trackdone'
GROUP BY t.name, t.artist
HAVING minutes_played >= 30
ORDER BY minutes_played DESC;
