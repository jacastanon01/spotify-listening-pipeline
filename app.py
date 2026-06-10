
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

from db import create_connection
from queries import GET_RAW_STREAMS_REASONS, GET_RAW_STREAMS_TIME, GET_YEARLY_PLAYS_MINUTES, GET_YEARLY_TOP_ARTISTS, GET_YEARLY_TOP_TRACKS

# ============================================================
# UTILITIES
# ============================================================

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

def calculate_minutes(row: pd.Series) -> int:
    return row["ms_played"] / 60000

def get_month_detail(streams_df: pd.DataFrame, tracks_df: pd.DataFrame, year: int, month: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask = (streams_df["year"] == year) & (streams_df["month_name"] == month)
    filtered = pd.merge(streams_df[mask], tracks_df, left_on="track_uri", right_on="uri")

    top_artists = (
        filtered.groupby("artist")["ms_played"]
        .sum()
        .reset_index()
        .sort_values("ms_played", ascending=False)
        .head(10)
    )
    top_artists["minutes"] = (top_artists["ms_played"] / 60000).round(1)

    top_tracks = (
        filtered.groupby(["name", "artist"])["ms_played"]
        .sum()
        .reset_index()
        .sort_values("ms_played", ascending=False)
        .head(10)
    )
    top_tracks["minutes"] = (top_tracks["ms_played"] / 60000).round(1)

    return top_artists, top_tracks

def render_month_detail_html(top_artists: pd.DataFrame, top_tracks: pd.DataFrame, month: str, year: int) -> str:
    def build_items(df: pd.DataFrame, name_col: str, subtitle_col: str | None = None) -> str:
        max_min = df["minutes"].max()
        rows = ""
        for i, row in enumerate(df.itertuples(), 1):
            name = getattr(row, name_col)
            minutes = row.minutes
            bar_width = int((minutes / max_min) * 100) if max_min > 0 else 0
            subtitle_html = ""
            if subtitle_col:
                subtitle = getattr(row, subtitle_col)
                subtitle_html = f'<div class="subtitle">{subtitle}</div>'
            rows += f"""
            <div class="item">
                <span class="rank">{i:02d}</span>
                <div class="info">
                    <div class="name" title="{name}">{name}</div>
                    {subtitle_html}
                    <div class="bar" style="width:{bar_width}%"></div>
                    <div class="minutes">{minutes:.0f} min</div>
                </div>
            </div>"""
        return rows

    return f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: transparent; font-family: 'Inter', system-ui, sans-serif; }}
        .container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 4px; }}
        .column {{ background: #1A1A24; border-radius: 12px; overflow: hidden; }}
        .column-header {{ padding: 14px 20px; border-bottom: 1px solid #2D2D3D; }}
        .column-title {{ font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #7C3AED; }}
        .item {{ display: flex; align-items: center; padding: 10px 20px; border-bottom: 1px solid #1F1F2E; gap: 14px; }}
        .item:last-child {{ border-bottom: none; }}
        .rank {{ font-size: 1.3rem; font-weight: 800; color: #2A2A3D; min-width: 28px; font-variant-numeric: tabular-nums; }}
        .info {{ flex: 1; min-width: 0; }}
        .name {{ font-size: 0.85rem; font-weight: 500; color: #E2E8F0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .subtitle {{ font-size: 0.72rem; color: #64748B; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .bar {{ height: 2px; background: #7C3AED; border-radius: 1px; margin-top: 5px; margin-bottom: 3px; }}
        .minutes {{ font-size: 0.7rem; color: #4A5568; letter-spacing: 0.04em; }}
    </style>
    <div class="container">
        <div class="column">
            <div class="column-header"><div class="column-title">Top Artists · {month} {year}</div></div>
            {build_items(top_artists, "artist")}
        </div>
        <div class="column">
            <div class="column-header"><div class="column-title">Top Tracks · {month} {year}</div></div>
            {build_items(top_tracks, "name", subtitle_col="artist")}
        </div>
    </div>"""


@st.cache_data
def get_monthly_played_stats(df: pd.DataFrame, year: int) -> pd.DataFrame:
    # Monthly aggrgation for bar chart
    monthly_df = (
        df[df["year"] == year] # filter to selected year
        .groupby(["month", "month_name"])["ms_played"] # group by month index and name 
        .sum() # sum ms_played for given months
        .reset_index()
    )
    monthly_df["minutes_played"] = monthly_df["ms_played"] / 60000
    return monthly_df

# ============================================================
# SETUP
# ============================================================


@st.cache_resource
def get_connection() -> sqlite3.Connection | None:
    conn = create_connection("listening_history.db", check_same_thread=False)
    return conn
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
def get_stream_reasons(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    return pd.read_sql_query(GET_RAW_STREAMS_REASONS, _conn)

@st.cache_data
def load_streams_with_time(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    time_df = pd.read_sql_query(GET_RAW_STREAMS_TIME, _conn)
    time_df["ts"] = pd.to_datetime(time_df["ts"], utc=True, format='ISO8601').dt.tz_convert("US/Central") # convert ts to central standard for accurate results
    time_df["year"] = time_df["ts"].dt.year # add year column
    time_df["month"] = time_df["ts"].dt.month # use for sorting
    time_df["month_name"] = time_df["ts"].dt.month_name() # add month name
    time_df["hour"] = time_df["ts"].dt.hour # add hour column
    return time_df

@st.cache_data
def load_tracks(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    return pd.read_sql_query("SELECT uri, name, artist FROM tracks", _conn)

@st.cache_data
def load_reasons(_conn: sqlite3.Connection | None) -> tuple:
    reasons_df = get_stream_reasons(_conn)

    start_reasons_df, end_reasons_df = reasons_df.copy(), reasons_df.copy() # copy() avoids reference in memory and allocates new space for both variables to operate on independently
    start_reasons_df["category"] = start_reasons_df["reason_start"].map(start_reasons_dict).fillna(other) # labels every row as "Deliberate", "Passive" or "Other" based on the reason_start column
    
    deliberate_filter = (start_reasons_df["reason_start"].isin( # isin() is a pandas method similar to the in keyword in Python
        ["fwdbtn", "backbtn"]) # instead of using x in [list], isin() contains similar logic, but allows filtering within Series
        ) & (start_reasons_df["reason_end"] == "trackdone") # Label "Deliberate" if user clicked to repeat song and listen in entirety
    
    start_reasons_df.loc[deliberate_filter, "category"] = deliberate # apply filter to category column and label "Deliberate"
    start_reasons_df = start_reasons_df.groupby("category").size().reset_index(name="count") # size() counts rows per category group, reset_index promotes result back to DataFrame
    
    end_reasons_df["category"] = end_reasons_df["reason_end"].map(end_reasons_dict).fillna(other) # Create cateogry column, used dictionary to populate values of column
    end_reasons_df = end_reasons_df.groupby("category").size().reset_index(name="count")

    return start_reasons_df, end_reasons_df


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

    time_df = get_minutes_by_year(conn, start_year, end_year)
    artist_df = get_top_artists_by_year(conn, start_year, end_year)
    tracks_df_year = get_top_tracks_by_year(conn, start_year, end_year)
    tracks_df_year["label"] = tracks_df_year["name"] + " - " + tracks_df_year["artist"]

    if time_df.empty:
        st.warning(f"No listening history found between {start_year} and {end_year}")
    else:
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








