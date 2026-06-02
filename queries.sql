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

-- How much time was spent listening to tracks per year
SELECT strftime('%Y', ts) as year, COUNT(*) as plays 
FROM streams 
JOIN tracks t ON streams.track_uri = t.uri 
WHERE t.artist != 'Sleepy Dogs' -- Excluding calming music I played for my dog at the time, which dominated 2022
GROUP BY year ORDER BY plays desc;


-- Top artists from the first peak listening period (2018-2019)
SELECT t.artist, COUNT(*) as plays
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2018', '2019')
GROUP BY t.artist
ORDER BY plays DESC
LIMIT 15;


-- Top tracks from the first peak listening period (2018-2019)
SELECT t.name, t.artist, COUNT(*) as plays
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2018', '2019')
GROUP BY t.name, t.artist
ORDER BY plays DESC
LIMIT 15;


-- Top artists from the recent listening period (2024-2026)
SELECT t.artist, COUNT(*) as plays
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2024', '2025', '2026')
GROUP BY t.artist
ORDER BY plays DESC
LIMIT 15;


-- Top tracks from the recent listening period (2024-2026)
SELECT t.name, t.artist, COUNT(*) as plays
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE strftime('%Y', s.ts) IN ('2024', '2025', '2026')
GROUP BY t.name, t.artist
ORDER BY plays DESC
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
-- Note: skip data only reliable from 2022 onward
SELECT t.name, t.artist, COUNT(*) as plays,
       ROUND(AVG(s.skipped) * 100, 1) as skip_rate_pct
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE s.skipped IS NOT NULL
GROUP BY t.name, t.artist
HAVING plays > 10 AND AVG(s.skipped) < 0.2
ORDER BY plays DESC
LIMIT 15;


-- Tracks played more than 10 times with a skip rate above 60%
-- Songs that keep getting queued up despite being skipped more
-- often than not. A different category from disliked songs.
-- Note: skip data only reliable from 2022 onward
SELECT t.name, t.artist, COUNT(*) as plays,
       ROUND(AVG(s.skipped) * 100, 1) as skip_rate_pct
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
WHERE s.skipped IS NOT NULL
GROUP BY t.name, t.artist
HAVING plays > 10 AND AVG(s.skipped) > 0.6
ORDER BY plays DESC
LIMIT 10;