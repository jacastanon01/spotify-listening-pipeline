import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

from db import create_connection
from queries import GET_RAW_STREAMS_TIME, GET_YEARLY_PLAYS_MINUTES, GET_YEARLY_TOP_ARTISTS, GET_YEARLY_TOP_TRACKS

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



# ============================================================
# APP LAYOUT
# ============================================================

overview, habits, phases = st.tabs(["Overview", "Habits", "Phases"])

# OVERVIEW
with overview:
    st.header("Music through the years")
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

    time_df = get_time_of_day_analysis(conn) # get raw data from sqlite

    time_df["ts"] = pd.to_datetime(time_df["ts"], utc=True, format='ISO8601').dt.tz_convert("US/Central") # convert ts to central standard for accurate results
    time_df["hour"] = time_df["ts"].dt.hour # add hour column

    time_df = time_df.groupby("hour")["ms_played"].sum() # Collapses all rows into 24 rows, one per hour, and sums ms_played
    time_df = time_df.reset_index() # converts grouped series (hour: ms_played) back to two column data frame with named columns

    time_df["ms_played"] = time_df["ms_played"] / 60000 # calcualtes minutes from milliseconds
    time_df = time_df.sort_values("hour") 
    time_df["hour"] = time_df["hour"].apply(lambda x: format_hour(int(x))) # formats 24 hour format on each row to 1-12 AM/PM

    hourly_fig = px.bar(time_df, x="hour", y="ms_played") # Sets up chart to refelect time played during each hour
    st.plotly_chart(hourly_fig)

