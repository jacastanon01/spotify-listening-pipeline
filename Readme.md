# Spotify Listening History Pipeline

A personal data pipeline that transforms Spotify's exported listening history into a queryable local database. Built to understand my own listening habits and rediscover why I enjoy building things that mean something to me.

---

## A Note on Process

This project was built collaboratively with Claude, Anthropic's AI. The architecture, schema design, and key engineering decisions were worked through in conversation, with Claude acting as a guide and sounding board. The code itself was written by me.

I came back to Python after a few years away from software. This project was less about proving I never forgot anything and more about remembering why I liked it in the first place. Like jumping back into a pool and rediscovering you prefer the breaststroke. The thinking came back faster than the syntax.

---

## Motivation

Spotify gives you access to your full listening history as JSON exports but does nothing useful with it analytically. I wanted a way to actually query that data, find patterns, and understand how my taste and habits have shifted over time. What started as a data exercise turned into something I actually wanted to finish.

---

## What It Does

Takes raw JSON files from Spotify's data export and loads them into a normalized SQLite database. The result is a queryable dataset covering years of listening history with behavioral metadata including play duration, skip events, and how each track was started and ended.

---

## Project Structure

```
project/
├── data/               # Spotify JSON export files (not committed)
├── main.py             # Entry point, orchestrates the pipeline
├── pipeline.py         # Data loading, filtering, and transformation
├── db.py               # Database connection, schema, and inserts
├── models.py           # Typed dataclasses representing the data
├── fetch_recent.py     # Spotify API live feed (see note below)
├── test_pipeline.py    # Unit tests
├── test_fetch_recent.py # Unit tests
├── requirements.txt
└── .gitignore
```

---

## Schema

Two normalized tables connected by a foreign key.

**tracks** stores one row per unique piece of content:

| Column | Type | Notes |
|--------|------|-------|
| uri | TEXT | Primary key, Spotify's unique identifier |
| name | TEXT | Track title |
| artist | TEXT | Artist name |
| album | TEXT | Album name |

**streams** stores one row per listening event:

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Auto-generated primary key |
| ts | TEXT | ISO 8601 timestamp |
| ms_played | INTEGER | Milliseconds actually listened |
| skipped | BOOLEAN | Whether the track was skipped |
| reason_start | TEXT | How playback started |
| reason_end | TEXT | How playback ended |
| track_uri | TEXT | Foreign key referencing tracks.uri |

---

## Design Decisions

**On keeping it simple.**
My instinct early on was to model this with more tables: separate ones for artists, albums, content types. That instinct wasn't wrong, it was just premature. Working through the schema in conversation with an AI helped me recognize I was over-engineering before I had real queries to justify the complexity. Two tables handle everything the analysis actually needs. The foreign key relationship between streams and tracks is where the interesting joins happen.

**On normalization.**
Track metadata like artist and album name repeats across every listening event. Storing it once in a tracks table and referencing it by URI keeps the data clean and makes aggregation queries straightforward. A stream record says what happened and when. A track record says what was played. Those are different things and belong in different places.

**On idempotency.**
The pipeline uses `INSERT OR IGNORE` throughout. Running it multiple times against the same files or overlapping exports never creates duplicate rows. This was a deliberate design choice that made the pipeline safe to run repeatedly as new export files arrive.

**On typed Python.**
Every data structure is a typed dataclass. The pipeline has a clear contract at each stage: raw JSON in, validated dataclasses out, dataclasses into the database. Required fields fail loudly if missing. Optional fields use `.get()` with appropriate defaults. This distinction between required and optional is visible in the code itself, not just in comments.

**Looking ahead: episodes and audiobooks.**
The current schema covers tracks only. Expanding to include podcast episodes and audiobooks from the export data is a natural next step. The behavioral fields, `ms_played`, `skipped`, `reason_start`, `reason_end`, are present for all content types in the export. The tracks table will need a `content_type` column and nullable fields for type-specific metadata. The streams table needs no changes. That asymmetry is intentional: listening behavior is the same regardless of what you're listening to.

---

## On the API Layer

`fetch_recent.py` was built to keep the database current between exports by pulling from Spotify's recently played endpoint. The implementation worked. The data did not.

A few things surfaced through actually using it and questioning the output:

Spotify's recently played endpoint has a documented inconsistency in what `played_at` actually represents. Sometimes it's when a track started. Sometimes it's when it ended. Spotify has an open issue on this going back to 2018 with no resolution.

The endpoint also has known phantom entry bugs, where tracks appear in the response that were never actually played, or were played for less than a second before the app was closed.

Most importantly: the endpoint returns no behavioral fields. No play duration, no skip status, no reason for starting or ending. The entire analytical value of this project depends on those fields.

Injecting thin, unreliable API data into a database built around behavioral analysis would corrupt the integrity of what the export data provides. The decision to scope the API layer out of production use wasn't a failure of implementation. It was a data quality decision made after actually interrogating the source.

`fetch_recent.py` remains in the project because the reasoning process is part of the work. In practice, periodic re-export from Spotify is the right approach for keeping the timeline current.

---

## Analytics

The goal was to find patterns across time, not just aggregate counts. Some questions this database can answer:

```sql
-- How my listening volume has shifted by month over the years
SELECT strftime('%Y-%m', ts) as month, 
       COUNT(*) as plays,
       SUM(ms_played) / 3600000.0 as hours_played
FROM streams
GROUP BY month
ORDER BY month;

-- What time of day I listen most
SELECT strftime('%H', ts) as hour, COUNT(*) as plays
FROM streams
GROUP BY hour
ORDER BY plays DESC;

-- Artists I went through phases with, high play counts in short windows
SELECT t.artist,
       strftime('%Y-%m', s.ts) as month,
       COUNT(*) as plays
FROM streams s
JOIN tracks t ON s.track_uri = t.uri
GROUP BY t.artist, month
HAVING plays > 20
ORDER BY plays DESC;


-- Intentional listening vs passive autoplay
SELECT reason_start, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
FROM streams
GROUP BY reason_start
ORDER BY count DESC;

-- How often I skip vs listen through by year
SELECT strftime('%Y', ts) as year,
       ROUND(AVG(skipped) * 100, 1) as skip_rate_pct
FROM streams
WHERE skipped IS NOT NULL
GROUP BY year
ORDER BY year;
```

---

## Running It Yourself

Request your extended streaming history from Spotify at Settings > Privacy > Download your data. Select Extended streaming history. Spotify emails it within a few days.

```bash
git clone https://github.com/jacastanon01/spotify-listening-pipeline.git
cd spotify-listening-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Drop your JSON files into the `data/` folder and run:

```bash
python main.py
```