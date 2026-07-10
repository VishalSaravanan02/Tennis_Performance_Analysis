"""Player Explorer — any player's history, surfaces and progression."""

import plotly.express as px
import streamlit as st

from utils import get_matches

st.set_page_config(page_title="Player Explorer", page_icon="🎾", layout="wide")
st.title("Player Explorer")

df = get_matches()

# ── Player selection ────────────────────────────────────────────
players = sorted(df["player_name"].unique())
default_ix = players.index("Novak Djokovic") if "Novak Djokovic" in players else 0
player = st.selectbox("Choose a player", players, index=default_ix)

matches = df[df["player_name"] == player].sort_values("tourney_date")

# ── KPI row ─────────────────────────────────────────────────────
best_win = matches[matches["win"] == 1].nsmallest(1, "opponent_rank")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches", len(matches))
col2.metric("Win rate", f"{matches['win'].mean()*100:.1f}%")
col3.metric("Best ranking in data", int(matches["player_rank"].min()))
col4.metric(
    "Best win (opp. rank)",
    int(best_win["opponent_rank"].iloc[0]) if not best_win.empty else "—",
    help="Lowest-ranked opponent beaten (lower = better opponent)",
)

if len(matches) < 10:
    st.caption(f"⚠️ Only {len(matches)} matches for {player} — interpret with caution.")

st.divider()

# ── Rank progression ────────────────────────────────────────────
st.subheader("Ranking over time")
fig = px.line(matches, x="tourney_date", y="player_rank", markers=True,
              labels={"tourney_date": "", "player_rank": "ATP rank"},
              hover_data=["tourney_name", "round"])
fig.update_yaxes(autorange="reversed")  # rank 1 at the top
st.plotly_chart(fig, use_container_width=True)

# ── Surface & round splits ──────────────────────────────────────
left, right = st.columns(2)

with left:
    st.subheader("Win rate by surface")
    surf = matches.groupby("surface")["win"].agg(["mean", "count"]).reset_index()
    surf["win_pct"] = (surf["mean"] * 100).round(1)
    fig = px.bar(surf, x="surface", y="win_pct", text="win_pct",
                 hover_data=["count"],
                 labels={"surface": "", "win_pct": "Win rate (%)"})
    fig.add_hline(y=50, line_dash="dash", line_color="red")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Win rate by round")
    round_order = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]
    rnd = matches.groupby("round")["win"].agg(["mean", "count"]).reset_index()
    rnd["win_pct"] = (rnd["mean"] * 100).round(1)
    rnd = rnd[rnd["round"].isin(round_order)]
    fig = px.bar(rnd, x="round", y="win_pct", text="win_pct",
                 hover_data=["count"],
                 category_orders={"round": round_order},
                 labels={"round": "", "win_pct": "Win rate (%)"})
    fig.add_hline(y=50, line_dash="dash", line_color="red")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ── Match history table ─────────────────────────────────────────
st.subheader("Match history")
history = matches[
    ["tourney_date", "tourney_name", "surface", "round",
     "opponent_rank", "score", "win"]
].sort_values("tourney_date", ascending=False)
history["result"] = history["win"].map({1: "✅ Won", 0: "❌ Lost"})
st.dataframe(
    history.drop(columns=["win"]),
    use_container_width=True,
    hide_index=True,
    column_config={
        "tourney_date": st.column_config.DateColumn("Date"),
        "tourney_name": "Tournament",
        "surface": "Surface",
        "round": "Round",
        "opponent_rank": "Opp. rank",
        "score": "Score",
        "result": "Result",
    },
)