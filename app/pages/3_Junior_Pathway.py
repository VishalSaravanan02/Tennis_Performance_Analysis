"""Junior Pathway — does junior performance predict senior success?"""

import plotly.express as px
import streamlit as st

from utils import get_matches
from src.config import MIN_MATCHES_PER_STAGE, STAGE_ORDER
from src.pathway import (
    assign_career_stage,
    stage_win_rates,
    nextgen_senior_correlation,
)

st.set_page_config(page_title="Junior Pathway", page_icon="🎾", layout="wide")
st.title("Junior Pathway")
st.markdown(
    "**The question:** what predicts a successful transition from junior to "
    "professional tennis — raw improvement speed, or consistency? "
    "Each match is classified by the player's age at the time: "
    "Junior (U18), Next Gen (19–21), Senior (21+)."
)

df = assign_career_stage(get_matches())

# ── Stage comparison ────────────────────────────────────────────
st.subheader("Win rate by career stage")
stages = stage_win_rates(df)
fig = px.bar(stages, x="career_stage", y="avg_win_rate", text="avg_win_rate",
             category_orders={"career_stage": STAGE_ORDER},
             hover_data=["player_count", "median_win_rate"],
             labels={"career_stage": "", "avg_win_rate": "Avg win rate (%)"})
fig.update_traces(texttemplate="%{text}%", textposition="outside")
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Player-level averages (each player's win rate computed first, then "
    "averaged) so high-volume players don't dominate."
)

st.divider()

# ── The headline finding, interactive ───────────────────────────
st.subheader("Does Next Gen performance predict Senior success?")

min_matches = st.slider(
    "Minimum matches required in each stage",
    min_value=3, max_value=15, value=MIN_MATCHES_PER_STAGE,
    help="Players need at least this many matches in BOTH Next Gen and "
         "Senior stages to be included. Higher = fewer players, more "
         "reliable per-player stats.",
)

result = nextgen_senior_correlation(df, min_matches=min_matches)

col1, col2, col3 = st.columns(3)
col1.metric("Players in analysis", result["n_players"])
col2.metric("Win-rate consistency → Senior success",
            f"r = {result['winrate_r']:.3f}",
            help=f"p = {result['winrate_p']:.5f}")
col3.metric("Improvement speed → Senior success",
            f"r = {result['improvement_r']:.3f}",
            help=f"p = {result['improvement_p']:.3f}")

players = result["players"]

left, right = st.columns(2)
with left:
    fig = px.scatter(players, x="nextgen_win_rate", y="senior_win_rate",
                     hover_name="player_name", trendline="ols",
                     labels={"nextgen_win_rate": "Next Gen win rate",
                             "senior_win_rate": "Senior win rate"},
                     title="Consistency predicts success")
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.scatter(players.dropna(subset=["nextgen_improvement"]),
                     x="nextgen_improvement", y="senior_win_rate",
                     hover_name="player_name", trendline="ols",
                     labels={"nextgen_improvement": "Next Gen improvement (%)",
                             "senior_win_rate": "Senior win rate"},
                     title="Improvement speed does not")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Methodology & caveats"):
    st.markdown(f"""
- At the default threshold ({MIN_MATCHES_PER_STAGE}+ matches per stage),
  **{nextgen_senior_correlation(df)["n_players"]} players** qualify — a modest
  sample. The finding is treated as a strong signal to validate on longer
  historical windows, not a definitive result.
- Move the slider to test sensitivity: if the correlation held only at one
  threshold, it would be fragile. Watch how r and n trade off.
- Win-rate correlation uses Pearson r on per-player stage win rates.
  Improvement = relative ranking change across the Next Gen stage.
""")