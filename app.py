
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

from data_funcs import  get_monthly_played_stats, load_reasons, load_streams_with_time, load_tracks
from db import create_connection
from utils import format_hour, get_month_detail, render_month_detail_html

# ============================================================
# SETUP
# ============================================================

@st.cache_resource
def get_connection() -> sqlite3.Connection | None:
    conn = create_connection("listening_history.db", check_same_thread=False)
    return conn
st.title("Listening History Project")
conn = get_connection()

streams_df = load_streams_with_time(conn)
tracks_df = load_tracks(conn)
start_reasons_df, end_reasons_df = load_reasons(conn)

# ============================================================
# APP LAYOUT
# ============================================================

overview, habits, phases = st.tabs(["Overview", "Habits", "Phases"])

# OVERVIEW
with overview:
    st.header("Listening volume through the years")
    start_year, end_year = st.slider("Time Range(Year)", 2013, 2026, (2013, 2026))

    year_mask = (streams_df["year"] >= start_year) & (streams_df["year"] <= end_year)
    filtered = pd.merge(streams_df[year_mask], tracks_df, left_on="track_uri", right_on="uri")

    if filtered.empty:
        st.warning(f"No listening history found between {start_year} and {end_year}")
    else:
        time_df = (
            filtered.groupby("year")["ms_played"]
            .sum()
            .reset_index()
            .sort_values("year", ascending=True)
        )
        time_df["minutes_played"] = (time_df["ms_played"] / 60000).round(1)
        time_df["year"] = time_df["year"].map(lambda x: str(x)) 

        artist_df = (
            filtered.groupby("artist")["ms_played"]
            .sum()
            .reset_index()
            .sort_values("ms_played", ascending=True)
            .tail(15)
        )
        artist_df["minutes_played"] = (artist_df["ms_played"] / 60000).round(1)

        tracks_df_year = (
            filtered.groupby(["name", "artist"])["ms_played"]
            .sum()
            .reset_index()
            .sort_values("ms_played", ascending=True)
            .tail(15)
        )
        tracks_df_year["minutes_played"] = (tracks_df_year["ms_played"] / 60000).round(1)
        tracks_df_year["label"] = tracks_df_year["name"] + " - " + tracks_df_year["artist"]

        st.line_chart(time_df, x="year", y="minutes_played")

        artists_fig = px.bar(artist_df, x="minutes_played", y="artist", orientation="h")
        st.plotly_chart(artists_fig)

        tracks_fig = px.bar(tracks_df_year, x="minutes_played", y="label", orientation="h")
        st.plotly_chart(tracks_fig)


with habits:
    st.header("How I listen")

    # TIME OF DAY BAR CHART
    st.subheader("When I listen most")

    # reset_index() converts grouped series (hour: ms_played) back to two column DataFrame with named columns
    time_df = streams_df.groupby("hour")["ms_played"].sum().reset_index() # Collapses all rows into 24 rows, one per hour, and sums ms_played

    time_df["minutes"] = time_df["ms_played"] / 60000 # calcualtes minutes from milliseconds
    time_df = time_df.sort_values("hour") 
    time_df["hour"] = time_df["hour"].apply(lambda x: format_hour(int(x))) # formats 24 hour format on each row to 1-12 AM/PM

    hourly_fig = px.bar(time_df, x="hour", y="minutes") # Sets up chart to refelect time played during each hour
    st.plotly_chart(hourly_fig)

    # REASON_START DONUT PIE CHART

    st.subheader("How I start listening")
    st.caption("What triggers a new track to play")

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
        st.markdown('<span style="color:#81D6EB; font-weight:bold; font-size:1.1em">● Passive</span>', unsafe_allow_html=True)
        st.caption("Tracks Spotify advanced to automatically after the previous one ended.")

    with col3:
        st.markdown('<span style="color:#78909C; font-weight:bold; font-size:1.1em">● Other</span>', unsafe_allow_html=True)
        st.caption("Skips you abandoned before finishing, app loads, remote sessions, and unclassified events.")
    
    # REASONS END DONUT PIE CHART

    st.subheader("How I end tracks")
    st.caption("Whether or not I let songs finish, skip ahead, or stop listening entirely")

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
    st.subheader("Select a year and month to see top artists and tracks")

    # Set up year selector
    available_years = sorted(streams_df["year"].unique(), reverse=True)
    selected_year = st.selectbox("Select a year", available_years)

    if selected_year is None:
        st.stop()

    if "selected_year" not in st.session_state:
        st.session_state["selected_year"] = selected_year
    if "selected_month" not in st.session_state:
        st.session_state["selected_month"] = None

    if st.session_state["selected_year"] != selected_year:
        st.session_state["selected_year"] = selected_year
        st.session_state["selected_month"] = None

    monthly_df = get_monthly_played_stats(streams_df, selected_year)
    yearly_fig = px.bar(monthly_df, x="month_name", y="minutes_played")
    event = st.plotly_chart(yearly_fig, on_select="rerun")
    points = event.get("selection", {}).get("points", [])

    if points:
        st.session_state["selected_month"] = event["selection"]["points"][0].get("x")

    if st.session_state.get("selected_month"):
        selected_month = st.session_state["selected_month"]

        filter_by_month_year = (
            streams_df["year"] == selected_year
            ) & (
                streams_df["month_name"] == selected_month
            )
        
        filtered_streams = pd.merge(left=streams_df[filter_by_month_year], right=tracks_df, left_on="track_uri", right_on="uri")
        filtered_artists = (
            filtered_streams
            .groupby("artist")["ms_played"]
            .sum()
            .reset_index()
            .sort_values("ms_played", ascending=False)
            .head(10)
        )
        filtered_artists["minutes"] = filtered_artists["ms_played"] / 60000

        filtered_tracks = (
            filtered_streams
            .groupby("name")["ms_played"]
            .sum()
            .reset_index()
            .sort_values("ms_played", ascending=False)
            .head(10)
        )
        filtered_tracks["minutes"] = filtered_tracks["ms_played"] / 60000

        if st.session_state.get("selected_month"):
            top_artists, top_tracks = get_month_detail(
                streams_df, tracks_df,
                st.session_state["selected_year"],
                st.session_state["selected_month"]
            )
            st.iframe(
                render_month_detail_html(top_artists, top_tracks, st.session_state["selected_month"], st.session_state["selected_year"]),
                height=580
            )








