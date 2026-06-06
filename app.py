import streamlit as st
import sqlite3
import pandas as pd

from db import create_connection
from queries import GET_YEARLY_PLAYS_MINUTES

# ============================================================
# SETUP
# ============================================================
@st.cache_resource
def get_connection() -> sqlite3.Connection | None:
    conn = create_connection("listening_history.db")
    return conn

st.title("Listening History Project")
conn = get_connection()


# ============================================================
# DATA FUNCTIONS
# ============================================================
@st.cache_data
def get_plays_by_year(_conn: sqlite3.Connection | None) -> pd.DataFrame:
    return pd.read_sql_query(GET_YEARLY_PLAYS_MINUTES, _conn)


# ============================================================
# LAYOUT
# ============================================================
plays_by_year_data = get_plays_by_year(conn)
st.write(plays_by_year_data)