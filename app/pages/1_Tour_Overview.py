"""Tour Overview — win rates, upsets and rankings across the tour."""

import plotly.express as px
import streamlit as st

from utils import get_matches
from src.analysis import (
    assign_rank_group,
    assign_points_gap_group,
    win_rate_by_group,
    upset_rate_by_group,
)

st.set_page_config(page_title="Tour Overview", page_icon="🎾", layout="wide")
st.title("Tour Overview")

df = assign_points_gap_group(assign_rank_group(get_matches()))
df["year"] = df["tourney_date"].dt.year

LEVEL_NAMES = {
    "G": "Grand Slam", "M": "Masters", "A": "ATP 250/500",
    "D": "Davis Cup", "T": "Team Events", "F": "Finals", "O": "Olympics",
}
df["level_name"] = df["tourney_level"].map(LEVEL_NAMES)

# ── Sidebar filters ─────────────────────────────────────────────
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Year", sorted(df["year"].unique()),
                               default=sorted(df["year"].unique()))
surfaces = st.sidebar.multiselect("Surface", sorted(df["surface"].unique()),
                                  default=sorted(df["surface"].unique()))
levels = st.sidebar.multiselect("Tournament level", sorted(df["level_name"].unique()),
                                default=sorted(df["level_name"].unique()))

filtered = df[
    df["year"].isin(years)
    & df["surface"].isin(surfaces)
    & df["level_name"].isin(levels)
]

if filtered.empty:
    st.warning("No matches for the selected filters — widen the selection.")
    st.stop()

# ── KPI row ─────────────────────────────────────────────────────
favourites = filtered[filtered["rank_diff"] < 0]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches", f"{len(filtered) // 2:,}")
col2.metric("Players", f"{filtered['player_name'].nunique():,}")
col3.metric("Favourite win rate", f"{favourites['win'].mean()*100:.1f}%",
            help="How often the higher-ranked player wins")
col4.metric("Upset rate", f"{(1 - favourites['win'].mean())*100:.1f}%")

st.divider()

# ── Charts ──────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Win rate by rank group")
    wr = win_rate_by_group(filtered, "rank_group")
    fig = px.bar(wr, x="rank_group", y="win_pct", text="win_pct",
                 labels={"rank_group": "", "win_pct": "Win rate (%)"})
    fig.add_hline(y=50, line_dash="dash", line_color="red",
                  annotation_text="50% baseline")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("How often does the favourite lose?")
    up = upset_rate_by_group(filtered)
    fig = px.bar(up, x="rank_group", y="upset_rate", text="upset_rate",
                 labels={"rank_group": "", "upset_rate": "Upset rate (%)"},
                 hover_data=["times_favourite", "times_upset"])
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Win rate by rank-points gap")
gap = win_rate_by_group(filtered, "points_gap_group")
fig = px.bar(gap, x="points_gap_group", y="win_pct", text="win_pct",
             labels={"points_gap_group": "", "win_pct": "Win rate (%)"},
             hover_data=["total_matches"])
fig.add_hline(y=50, line_dash="dash", line_color="red")
fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Points gap captures quality magnitude, not just ordinal rank — "
    "the strongest single predictor in the dataset."
)