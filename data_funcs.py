import sqlite3
import streamlit as st
import pandas as pd

from queries import GET_RAW_STREAMS_REASONS, GET_RAW_STREAMS_TIME, GET_YEARLY_PLAYS_MINUTES, GET_YEARLY_TOP_ARTISTS, GET_YEARLY_TOP_TRACKS
from utils import DELIBERATE, END_REASONS_DICT, OTHER, START_REASONS_DICT


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
    start_reasons_df["category"] = start_reasons_df["reason_start"].map(START_REASONS_DICT).fillna(OTHER) # labels every row as "Deliberate", "Passive" or "Other" based on the reason_start column
    
    deliberate_filter = (start_reasons_df["reason_start"].isin( # isin() is a pandas method similar to the in keyword in Python
        ["fwdbtn", "backbtn"]) # instead of using x in [list], isin() contains similar logic, but allows filtering within Series
        ) & (start_reasons_df["reason_end"] == "trackdone") # Label "Deliberate" if user clicked to repeat song and listen in entirety
    
    start_reasons_df.loc[deliberate_filter, "category"] = DELIBERATE # apply filter to category column and label "Deliberate"
    start_reasons_df = start_reasons_df.groupby("category").size().reset_index(name="count") # size() counts rows per category group, reset_index promotes result back to DataFrame
    
    end_reasons_df["category"] = end_reasons_df["reason_end"].map(END_REASONS_DICT).fillna(OTHER) # Create cateogry column, used dictionary to populate values of column
    end_reasons_df = end_reasons_df.groupby("category").size().reset_index(name="count")

    return start_reasons_df, end_reasons_df

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
