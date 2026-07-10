"""Tennis Performance Analysis — dashboard home page."""

import streamlit as st

from utils import get_matches, get_model_bundle

st.set_page_config(
    page_title="Tennis Performance Analysis",
    page_icon="🎾",
    layout="wide",
)

st.title("🎾 Tennis Performance Analysis")
st.markdown(
    "Interactive analysis of ATP tour data (2022–2024): ranking dynamics, "
    "player development, junior pathways and ML match prediction. "
    "Built on Jeff Sackmann's tennis_atp dataset."
)

df = get_matches()
bundle = get_model_bundle()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches analysed", f"{len(df) // 2:,}")
col2.metric("Players covered", f"{df['player_name'].nunique():,}")
col3.metric("Model accuracy", f"{bundle['metrics']['accuracy']*100:.1f}%",
            help="XGBoost on held-out 2024 season; naive baseline 63.9%")
col4.metric("Headline finding", "r = 0.718",
            help="Next Gen win-rate consistency predicts Senior success (n=24, p<0.001)")

st.divider()

st.markdown("""
**Pages** (sidebar):
- **Tour Overview** — win rates, upsets and rankings across the tour
- **Player Explorer** — any player's history, surfaces and progression
- **Junior Pathway** — does junior performance predict senior success?
- **Match Predictor** — live win-probability predictions from the trained model
""")