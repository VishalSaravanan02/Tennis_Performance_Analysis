"""Match Predictor — live win probabilities from the trained model."""

import pandas as pd
import streamlit as st

from utils import get_model_bundle
from src.model import predict_match

st.set_page_config(page_title="Match Predictor", page_icon="🎾", layout="wide")
st.title("Match Predictor")
st.markdown(
    "Win-probability predictions from an XGBoost model trained on 2022–23 "
    "and evaluated on the held-out 2024 season."
)

bundle = get_model_bundle()
snapshot = bundle["player_snapshot"]

SURFACES = ["Hard", "Clay", "Grass"]
ROUNDS = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]


def stats_from_snapshot(player: str, surface: str) -> dict:
    row = snapshot.loc[player]
    surface_wr = row.get(f"winrate_{surface}")
    return {
        "rank": row["player_rank"],
        "rank_points": row["player_rank_points"],
        "recent_win_rate": row["recent_win_rate"],
        "surface_win_rate": 0.5 if pd.isna(surface_wr) else surface_wr,
        "fatigue_score_7": row["fatigue_score_7"],
    }


mode = st.radio("Input mode", ["Pick real players", "Manual scenario"],
                horizontal=True)

left, mid, right = st.columns([2, 1, 2])

if mode == "Pick real players":
    players = sorted(snapshot.index)
    with left:
        st.subheader("Player 1")
        p1_name = st.selectbox("Player 1", players,
                               index=players.index("Carlos Alcaraz")
                               if "Carlos Alcaraz" in players else 0,
                               label_visibility="collapsed")
    with right:
        st.subheader("Player 2")
        p2_name = st.selectbox("Player 2", players,
                               index=players.index("Jannik Sinner")
                               if "Jannik Sinner" in players else 1,
                               label_visibility="collapsed")
    with mid:
        st.subheader("Context")
        surface = st.selectbox("Surface", SURFACES)
        round_name = st.selectbox("Round", ROUNDS, index=6)

    if p1_name == p2_name:
        st.warning("Pick two different players.")
        st.stop()

    p1 = stats_from_snapshot(p1_name, surface)
    p2 = stats_from_snapshot(p2_name, surface)
    st.caption(
        "Player stats (rank, points, form, fatigue) are each player's most "
        "recent values in the dataset (through 2024)."
    )

else:
    with left:
        st.subheader("Player 1")
        p1 = {
            "rank": st.number_input("Rank (P1)", 1, 2000, 5),
            "rank_points": st.number_input("Rank points (P1)", 0, 20000, 5000),
            "recent_win_rate": st.slider("Recent win rate (P1)", 0.0, 1.0, 0.7),
            "surface_win_rate": st.slider("Surface win rate (P1)", 0.0, 1.0, 0.65),
            "fatigue_score_7": st.slider("Fatigue score (P1)", 0.0, 1.0, 0.3),
        }
    with right:
        st.subheader("Player 2")
        p2 = {
            "rank": st.number_input("Rank (P2)", 1, 2000, 50),
            "rank_points": st.number_input("Rank points (P2)", 0, 20000, 1000),
            "recent_win_rate": st.slider("Recent win rate (P2)", 0.0, 1.0, 0.5),
            "surface_win_rate": st.slider("Surface win rate (P2)", 0.0, 1.0, 0.5),
            "fatigue_score_7": st.slider("Fatigue score (P2)", 0.0, 1.0, 0.3),
        }
    with mid:
        st.subheader("Context")
        surface = st.selectbox("Surface", SURFACES)
        round_name = st.selectbox("Round", ROUNDS, index=2)
    p1_name, p2_name = "Player 1", "Player 2"

st.divider()

if st.button("Predict", type="primary", use_container_width=True):
    p1_prob = predict_match(bundle, p1, p2, surface, round_name)
    p2_prob = predict_match(bundle, p2, p1, surface, round_name)
    # Normalise the two perspectives into one consistent probability
    total = p1_prob + p2_prob
    p1_final = p1_prob / total if total > 0 else 0.5

    col1, col2 = st.columns(2)
    col1.metric(p1_name, f"{p1_final*100:.1f}%")
    col2.metric(p2_name, f"{(1-p1_final)*100:.1f}%")
    st.progress(p1_final)

    st.caption(
        f"Model accuracy on the held-out 2024 season: "
        f"{bundle['metrics']['accuracy']*100:.1f}% vs a "
        f"{bundle['metrics']['baseline']['accuracy']*100:.1f}% ranking-only "
        "baseline. Tennis outcomes are inherently high-variance — treat "
        "probabilities as directional, not definitive."
    )

    st.caption(
        "Predictions are most reliable for typical scenarios; extreme inputs "
        "(perfect recent form, maximal points gaps) sit in sparse regions of "
        "the training data where the model extrapolates."
    )