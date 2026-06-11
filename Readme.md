# Spotify Listening History Analytics

A personal data pipeline and analytics dashboard that transforms Spotify's exported listening history into a queryable local database and interactive visualization app. Built to understand my own listening habits across nearly a decade of data and rediscover why I enjoy building things that mean something to me.

---

**Overview**

<img width="787" height="1296" alt="Screenshot 2026-06-11 at 4 20 23 PM" src="https://github.com/user-attachments/assets/1dcae336-a012-4e01-aba2-048c89bc61bb" />

**Habits**

<img width="812" height="1287" alt="Screenshot 2026-06-11 at 4 10 08 PM" src="https://github.com/user-attachments/assets/4b76b03b-6d2c-4b24-b23d-a69615f7a566" />

**Phases**

<img width="762" height="1302" alt="Screenshot 2026-06-11 at 4 18 36 PM" src="https://github.com/user-attachments/assets/46ef3c85-798f-4318-b6fd-a871f40dba24" />




---

## A Note on Process

This project was built collaboratively with Claude, Anthropic's AI. The architecture, schema design, and key engineering decisions were worked through in conversation, with Claude acting as a guide and sounding board. The code itself was written by me.

I came back to Python after a few years away from software. This project was less about proving I never forgot anything and more about remembering why I liked it in the first place. Like jumping back into a pool and rediscovering you prefer the breaststroke. The thinking came back faster than the syntax.

---

## Motivation

Spotify gives you access to your full listening history as JSON exports but does nothing useful with it analytically. I wanted a way to actually query that data, find patterns, and understand how my taste and habits have shifted over time. What started as a data exercise turned into something I actually wanted to finish.

---

## What It Does

**The pipeline** takes raw JSON files from Spotify's data export and loads them into a normalized SQLite database. The result is a queryable dataset covering years of listening history with behavioral metadata including play duration, skip events, and how each track was started and ended.

**The dashboard** is a Streamlit app with three tabs built on top of that database:

- **Overview** — Listening volume by year with a range slider, top artists, and top tracks
- **Habits** — Time of day bar chart with timezone-corrected local hours, reason_start and reason_end donut charts showing deliberate vs passive listening behavior
- **Phases** — Year and month selector showing a time capsule view of top artists and tracks for any given month in the listening history

---

## Project Structure

```
project/
├── data/                  # Spotify JSON export files (not committed)
├── app.py                 # Streamlit app layout and tab logic
├── data_funcs.py          # Cached data loading and preprocessing functions
├── utils.py               # Pure helper functions and HTML renderers
├── queries.py             # SQL strings for raw table queries
├── main.py                # Pipeline entry point
├── pipeline.py            # Data loading, filtering, and transformation
├── db.py                  # Database connection, schema, and inserts
├── models.py              # Typed dataclasses representing the data
├── fetch_recent.py        # Spotify API live feed (see note below)
├── test_pipeline.py       # Unit tests
├── test_fetch_recent.py   # Unit tests
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
| ts | TEXT | ISO 8601 timestamp in UTC |
| ms_played | INTEGER | Milliseconds actually listened |
| skipped | BOOLEAN | Whether the track was skipped |
| reason_start | TEXT | How playback started |
| reason_end | TEXT | How playback ended |
| track_uri | TEXT | Foreign key referencing tracks.uri |

---

## Design Decisions

**On keeping it simple.**
My instinct early on was to model this with more tables: separate ones for artists, albums, content types. That instinct wasn't wrong, it was just premature. Working through the schema helped me recognize I was over-engineering before I had real queries to justify the complexity. Two tables handle everything the analysis actually needs.

**On normalization.**
Track metadata like artist and album name repeats across every listening event. Storing it once in a tracks table and referencing it by URI keeps the data clean and makes aggregation queries straightforward. A stream record says what happened and when. A track record says what was played. Those are different things and belong in different places.

**On idempotency.**
The pipeline uses `INSERT OR IGNORE` throughout. Running it multiple times against the same files or overlapping exports never creates duplicate rows. This was a deliberate design choice that makes the pipeline safe to run repeatedly as new export files arrive.

**On typed Python.**
Every data structure is a typed dataclass. The pipeline has a clear contract at each stage: raw JSON in, validated dataclasses out, dataclasses into the database. Required fields fail loudly if missing. Optional fields use `.get()` with appropriate defaults.

**On timezone correctness.**
All timestamps are stored in UTC. The dashboard converts them to US/Central before any grouping or aggregation. This is a non-negotiable correctness requirement: extracting hours directly from UTC timestamps would systematically misrepresent listening behavior. A stream played at 8 AM local time stores as 14:00 UTC. Without conversion, the dashboard would report it as an afternoon listen. Every time-based chart in the Habits and Phases tabs is built on timezone-corrected data.

**On moving aggregations from SQL to pandas.**
Early versions of the overview tab ran parameterized SQL queries on every slider interaction, hitting the database on every rerun. The refactored version loads raw streams and tracks into memory once using `@st.cache_data`, then filters and aggregates entirely in pandas. Slider changes are cheap in-memory operations rather than database round trips.

**On data quality.**
The `skipped` field defaults to 0 rather than NULL for streams before 2023, making it unreliable as a behavioral signal for most of the dataset. The `reason_start` and `reason_end` fields are present and populated across the full history and are the more reliable behavioral signals. Findings that depend on skip data are scoped to 2023 onward.

**Looking ahead: episodes and audiobooks.**
The current schema covers tracks only. Expanding to include podcast episodes and audiobooks is a natural next step. The behavioral fields are present for all content types in the export. The tracks table would need a `content_type` column and nullable fields for type-specific metadata. The streams table needs no changes.

---

## On the API Layer

`fetch_recent.py` was built to keep the database current between exports by pulling from Spotify's recently played endpoint. The implementation worked. The data did not.

Spotify's recently played endpoint has a documented inconsistency in what `played_at` represents. Sometimes it is when a track started, sometimes when it ended. The endpoint also has known phantom entry bugs and returns no behavioral fields: no play duration, no skip status, no reason for starting or ending. The entire analytical value of this project depends on those fields.

Injecting thin, unreliable API data into a database built around behavioral analysis would corrupt the integrity of what the export data provides. The decision to scope the API layer out of production use was a data quality decision made after actually interrogating the source.

`fetch_recent.py` remains in the project because the reasoning process is part of the work. In practice, periodic re-export from Spotify is the right approach for keeping the timeline current.

---

## Running It Yourself

1. **Request data from Spotify**

Request your extended streaming history from Spotify at Settings > [Privacy](https://www.spotify.com/us/account/privacy/) > Download your data. Select Extended streaming history. Spotify emails it within a few days.

2. **Initialize the project**

```bash
git clone https://github.com/jacastanon01/spotify-listening-pipeline.git
cd spotify-listening-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Import data into project directory**
 
Create an empty directory and name it `data` or something similar. Open `main.py` and confirm the new directory name matches the string set in the `DATA_DIR` variable. Drop your JSON files into the new folder and run the pipeline:

```bash
python main.py
```

3. **Run app**
Confirm the `listening_history.db` sqlite database was created in your root directory. Then launch the dashboard:
```bash
streamlit run app.py
```
