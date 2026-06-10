import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

from db import create_connection
from queries import GET_RAW_STREAMS_REASONS, GET_RAW_STREAMS_TIME, GET_YEARLY_PLAYS_MINUTES, GET_YEARLY_TOP_ARTISTS, GET_YEARLY_TOP_TRACKS

# ============================================================
# SETUP
# ============================================================
@st.cache_resource
def get_connection() -> sqlite3.Connection | None:
    conn = create_connection("listening_history.db", check_same_thread=False)
    return conn

def format_hour(hour: int) -> str:
    period = "AM" if hour < 12 else "PM"
    display = hour % 12 or 12
    return f"{display}{period}"

deliberate, passive, other = ["Deliberate", "Passive", "Other"]
start_reasons_dict = {
    "clickrow": deliberate,
    "playbtn": deliberate,
    "trackdone": passive,
}
end_reasons_dict = {
    "trackdone": "Finished",
    "fwdbtn": "Skipped",
    "endplay": "Stopped"
}

def classify_start_reason(row: pd.Series) -> str:
    if row["reason_start"] in ["fwdbtn", "backbtn"] and row["reason_end"] == "trackdone":  # if user clicked to repeat song and listen in entirety
        return deliberate
    return start_reasons_dict.get(row["reason_start"], other)

st.title("Listening History Project")
conn = get_connection()


# ============================================================
# DATA FUNCTIONS
# ============================================================
@st.cache_data
def get_minutes_by_year(_conn: sqlite3.Connection | None, start_year: int = 2013, end_year: int = 2026) -> pd.DataFrame:
    return pd.read_sql_query(GET_YEARLY_PLAYS_MINUTES, _conn, params=[start_year, end_year])

@st.cache_data
def get_top_artists_by_year(_conn: sqlite3.Connection | None, start_year: int = 2013, end_year: int = 2026) -> pd.DataFrame:
    return pd.read_sql_query(GET_YEARLY_TOP_ARTISTS, _conn, params=[start_year, end_year])

@st.cache_data
def get_top_tracks_by_year(_conn: sqlite3.Connection | None, start_year: int = 2013, end_year: int = 2026) -> pd.DataFrame:
    return pd.read_sql_query(GET_YEARLY_TOP_TRACKS, _conn, params=[start_year, end_year])

@st.cache_data
def get_time_of_day_analysis(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    return pd.read_sql_query(GET_RAW_STREAMS_TIME, _conn)

@st.cache_data
def get_stream_reasons(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    return pd.read_sql_query(GET_RAW_STREAMS_REASONS, _conn)

@st.cache_data
def load_streams_with_time(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    time_df = get_time_of_day_analysis(_conn)
    time_df["ts"] = pd.to_datetime(time_df["ts"], utc=True, format='ISO8601').dt.tz_convert("US/Central") # convert ts to central standard for accurate results
    time_df["year"] = time_df["ts"].dt.year # add year column
    time_df["month"] = time_df["ts"].dt.month # add month column
    time_df["hour"] = time_df["ts"].dt.hour # add hour column
    return time_df

times = load_streams_with_time(conn)
print(times[0:5].info(verbose=True))



# ============================================================
# APP LAYOUT
# ============================================================

overview, habits, phases = st.tabs(["Overview", "Habits", "Phases"])

# OVERVIEW
with overview:
    st.header("Listening volume through the years")
    start_year, end_year = st.slider("Time Range(Year)", 2013, 2026, (2013, 2026))

    time_df = get_minutes_by_year(conn, start_year, end_year)
    artist_df = get_top_artists_by_year(conn, start_year, end_year)
    tracks_df = get_top_tracks_by_year(conn, start_year, end_year)
    tracks_df["label"] = tracks_df["name"] + " - " + tracks_df["artist"]

    if time_df.empty:
        st.warning(f"No listening history found between {start_year} and {end_year}")
    else:
        st.line_chart(time_df, x="year", y="minutes_played")

        artists_fig = px.bar(artist_df, x="minutes_played", y="artist", orientation="h")
        st.plotly_chart(artists_fig)

        tracks_fig = px.bar(tracks_df, x="minutes_played", y="label", orientation="h")
        st.plotly_chart(tracks_fig)

with habits:
    st.header("How I listen")

    # TIME OF DAY BAR CHART
    st.subheader("When I listen most")

    time_df = get_time_of_day_analysis(conn) # get raw data from sqlite
    time_df["ts"] = pd.to_datetime(time_df["ts"], utc=True, format='ISO8601').dt.tz_convert("US/Central") # convert ts to central standard for accurate results
    time_df["hour"] = time_df["ts"].dt.hour # add hour column


    time_df = time_df.groupby("hour")["ms_played"].sum() # Collapses all rows into 24 rows, one per hour, and sums ms_played
    time_df = time_df.reset_index() # converts grouped series (hour: ms_played) back to two column DataFrame with named columns

    time_df["minutes"] = time_df["ms_played"] / 60000 # calcualtes minutes from milliseconds
    time_df = time_df.sort_values("hour") 
    time_df["hour"] = time_df["hour"].apply(lambda x: format_hour(int(x))) # formats 24 hour format on each row to 1-12 AM/PM

    hourly_fig = px.bar(time_df, x="hour", y="minutes") # Sets up chart to refelect time played during each hour
    st.plotly_chart(hourly_fig)

    # REASON_START DONUT PIE CHART

    st.subheader("How I start listening")
    st.caption("What triggers a new track to play")

    start_reasons_df = get_stream_reasons(conn) # extract reason_start and reason_end from streams table
    start_reasons_df["category"] = start_reasons_df.apply(lambda x: classify_start_reason(x), axis=1) # axis = 1 applies classifiy_start_reason function row by row to access multiple columns (row["reason_start"] and row["reason_end"]) per row
    start_reasons_df = start_reasons_df.groupby("category").size().reset_index(name="count") # size() counts rows per category group, reset_index promotes result back to DataFrame

    reasons_fig = px.pie(
        start_reasons_df,
        values="count",
        names="category",
        hole=0.4,
        color_discrete_map={
            "Deliberate": "#2196F3",
            "Passive": "#81D6EB",
            "Other": "#78909C"
        }
    )
    reasons_fig.update_traces(marker=dict(colors=["#2196F3", "#78909C", "#81D6EB"])) # sets colors directly in order so no mismatched colors in chart or key ore markdown
    st.plotly_chart(reasons_fig)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<span style="color:#2196F3; font-weight:bold; font-size:1.1em">● Deliberate</span>', unsafe_allow_html=True)
        st.caption("Tracks you actively chose: clicked, pressed play, or skipped to and finished.")

    with col2:
        st.markdown('<span style="color:#B0BEC5; font-weight:bold; font-size:1.1em">● Passive</span>', unsafe_allow_html=True)
        st.caption("Tracks Spotify advanced to automatically after the previous one ended.")

    with col3:
        st.markdown('<span style="color:#78909C; font-weight:bold; font-size:1.1em">● Other</span>', unsafe_allow_html=True)
        st.caption("Skips you abandoned before finishing, app loads, remote sessions, and unclassified events.")
    
    # REASONS END DONUT PIE CHART

    st.subheader("How I end tracks")
    st.caption("Whether or not I let songs finish, skip ahead, or stop listening entirely")

    end_reasons_df = get_stream_reasons(conn)
    end_reasons_df["category"] = end_reasons_df["reason_end"].map(end_reasons_dict).fillna("Other") # Create cateogry column, used dictionary to populate values of column
    end_reasons_df = end_reasons_df.groupby("category").size().reset_index(name="count")

    end_reasons_fig = px.pie(
        end_reasons_df,
        values="count",
        names="category",
        hole=0.4,
        color_discrete_map={
            "Finished": "#4CAF50",
            "Skipped": "#FF9800",
            "Stopped": "#F44336",
            "Other": "#78909C"
        }
    )
    end_reasons_fig.update_traces(marker=dict(colors=["#4CAF50", "#78909C", "#FF9800", "#F44336"]))
    st.plotly_chart(end_reasons_fig)
    col1, col2, col3, col4 = st.columns(4)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<span style="color:#4CAF50; font-weight:bold; font-size:1.1em">● Finished</span>', unsafe_allow_html=True)
        st.caption("Track played to completion.")

    with col2:
        st.markdown('<span style="color:#FF9800; font-weight:bold; font-size:1.1em">● Skipped</span>', unsafe_allow_html=True)
        st.caption("Jumped forward before the track ended.")

    with col3:
        st.markdown('<span style="color:#F44336; font-weight:bold; font-size:1.1em">● Stopped</span>', unsafe_allow_html=True)
        st.caption("Playback ended before the track finished.")

    with col4:
        st.markdown('<span style="color:#78909C; font-weight:bold; font-size:1.1em">● Other</span>', unsafe_allow_html=True)
        st.caption("Back navigation, unexpected exits, and unclassified events.")

with phases:
    st.header("What was I listening to when")




