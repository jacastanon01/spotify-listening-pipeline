import unicodedata

import pandas as pd
from unicodedata import normalize

DELIBERATE, PASSIVE, OTHER = ["Deliberate", "Passive", "Other"]

START_REASONS_DICT= {
    "clickrow": DELIBERATE,
    "playbtn": DELIBERATE,
    "trackdone": PASSIVE,
}

END_REASONS_DICT = {
    "trackdone": "Finished",
    "fwdbtn": "Skipped",
    "endplay": "Stopped"
}


def format_hour(hour: int) -> str:
    """
    Convert a 24-hour integer to a readable 12-hour AM/PM label.
    :param hour: Integer hour value between 0 and 23.
    :return: Formatted string such as '12AM', '4PM', or '11AM'.
    """
    period = "AM" if hour < 12 else "PM"
    display = hour % 12 or 12
    return f"{display}{period}"

def get_month_detail(streams_df: pd.DataFrame, tracks_df: pd.DataFrame, year: int, month: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filter streams by year and month, merge with track metadata, and return
    top 10 artists and top 10 tracks ranked by total minutes played.
    :param streams_df: Cached DataFrame of all streams with timezone-converted timestamps.
    :param tracks_df: Cached DataFrame of track metadata including name and artist.
    :param year: The selected year as an integer.
    :param month: The selected month as a full name string, e.g. 'January'.
    :return: Tuple of (top_artists, top_tracks) DataFrames each with minutes column.
    """
    mask = (streams_df["year"] == year) & (streams_df["month_name"] == month)
    filtered = pd.merge(streams_df[mask], tracks_df, left_on="track_uri", right_on="uri")

    top_artists = (
        filtered.groupby("artist")["ms_played"]
        .sum()
        .reset_index()
        .sort_values("ms_played", ascending=False)
        .head(15)
    )
    top_artists["minutes"] = (top_artists["ms_played"] / 60000).round(1)

    top_tracks = (
        filtered.groupby(["name", "artist"])["ms_played"]
        .sum()
        .reset_index()
        .sort_values("ms_played", ascending=False)
        .head(15)
    )
    top_tracks["minutes"] = (top_tracks["ms_played"] / 60000).round(1)

    return top_artists, top_tracks

def render_month_detail_html(top_artists: pd.DataFrame, top_tracks: pd.DataFrame, month: str, year: int) -> str:
    """
    Generate an HTML string rendering top artists and top tracks side by side
    in a styled two-column card layout with proportional listening time bars.
    :param top_artists: DataFrame with columns 'artist' and 'minutes'.
    :param top_tracks: DataFrame with columns 'name', 'artist', and 'minutes'.
    :param month: The selected month as a full name string, e.g. 'January'.
    :param year: The selected year as an integer.
    :return: HTML string suitable for rendering via st.iframe.
    """
    def build_items(df: pd.DataFrame, name_col: str, subtitle_col: str | None = None) -> str:
        """
        Build HTML item rows for a ranked list, optionally with a subtitle line.
        :param df: DataFrame containing the ranked items.
        :param name_col: Column name to use as the primary display label.
        :param subtitle_col: Optional column name to render as a secondary line beneath the name.
        :return: HTML string of all item rows.
        """
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

def normalize_artist(artist_str: str | None) -> str:
    """
    takes a string and normalizes it by clearing whitespace, stripping punctuation, setting letters to lower case, etc
    :param artist_str: string of artist name 
    :return: string that sets standard for artist
    """
    if artist_str is None: 
        return "unknown artist"
    normalized = normalize('NFC', artist_str)
    stripped = ''.join(
        c for c in normalized # comparing each character
        # unicodedata.category() returns the Unicode category of a character. All punctuation categories start with 'P'
        if not unicodedata.category(c).startswith("P") 
    )
    return stripped.lower().strip()
