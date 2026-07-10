"""
Junior pathway analysis functions.

Extracted from notebooks/03_junior_pathway. Classifies matches by career
stage based on the player's age at the time of the match, and analyses
the Next Gen -> Senior transition.
"""

import numpy as np
import pandas as pd
from scipy import stats

from src.config import (
    JUNIOR_MAX_AGE,
    NEXTGEN_MAX_AGE,
    STAGE_JUNIOR,
    STAGE_NEXTGEN,
    STAGE_SENIOR,
    MIN_MATCHES_PER_STAGE,
)


def assign_career_stage(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a 'career_stage' column based on player_age."""
    out = df.copy()
    conditions = [
        out["player_age"] <= JUNIOR_MAX_AGE,
        out["player_age"] <= NEXTGEN_MAX_AGE,
    ]
    choices = [STAGE_JUNIOR, STAGE_NEXTGEN]
    out["career_stage"] = np.select(conditions, choices, default=STAGE_SENIOR)
    return out


def stage_win_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Win rate statistics per career stage, averaged at the player level.

    Each player's win rate is computed per stage first, then averaged
    across players — so high-volume Senior players do not dominate the
    stage aggregate (see notebooks/03).

    Returns: career_stage, avg_win_rate, median_win_rate, std_win_rate,
    player_count (win rates in %).
    """
    per_player = (
        df.groupby(["player_name", "career_stage"])["win"].mean().reset_index()
    )
    per_player.columns = ["player_name", "career_stage", "win_rate"]

    result = (
        per_player.groupby("career_stage")
        .agg(
            avg_win_rate=("win_rate", "mean"),
            median_win_rate=("win_rate", "median"),
            std_win_rate=("win_rate", "std"),
            player_count=("win_rate", "count"),
        )
        .reset_index()
    )
    result["avg_win_rate"] = (result["avg_win_rate"] * 100).round(2)
    result["median_win_rate"] = (result["median_win_rate"] * 100).round(2)
    result["std_win_rate"] = (result["std_win_rate"] * 100).round(2)
    return result


def relative_improvement_by_stage(
    df: pd.DataFrame, min_matches: int = MIN_MATCHES_PER_STAGE
) -> pd.DataFrame:
    """
    Relative ranking improvement per player per stage.

    Relative improvement = (rank_start - rank_end) / rank_start * 100,
    computed over each player's matches in date order within a stage.
    Positive = improved. Players with fewer than min_matches in a stage
    are excluded.

    Returns: player_name, career_stage, relative_improvement_rate, matches.
    """
    def _rel_improvement(group: pd.DataFrame) -> pd.Series:
        group = group.sort_values("tourney_date")
        rank_start = group["player_rank"].iloc[0]
        rank_end = group["player_rank"].iloc[-1]
        rate = (
            np.nan
            if (len(group) < min_matches or rank_start == 0)
            else round((rank_start - rank_end) / rank_start * 100, 2)
        )
        return pd.Series(
            {"relative_improvement_rate": rate, "matches": len(group)}
        )

    result = (
        df.groupby(["player_name", "career_stage"])
        .apply(_rel_improvement, include_groups=False)
        .reset_index()
    )
    return result.dropna(subset=["relative_improvement_rate"])


def nextgen_senior_correlation(
    df: pd.DataFrame, min_matches: int = MIN_MATCHES_PER_STAGE
) -> dict:
    """
    Does Next Gen performance predict Senior performance?

    For players with at least min_matches matches in BOTH stages,
    correlates Next Gen win rate (and Next Gen relative improvement)
    with Senior win rate.

    Returns a dict with:
        n_players, winrate_r, winrate_p, improvement_r, improvement_p,
        and 'players' (the per-player transition dataframe).
    """
    df = assign_career_stage(df) if "career_stage" not in df.columns else df

    rows = []
    for player, g in df.groupby("player_name"):
        nextgen = g[g["career_stage"] == STAGE_NEXTGEN]
        senior = g[g["career_stage"] == STAGE_SENIOR]
        if len(nextgen) >= min_matches and len(senior) >= min_matches:
            ng_sorted = nextgen.sort_values("tourney_date")
            rank_start = ng_sorted["player_rank"].iloc[0]
            rank_end = ng_sorted["player_rank"].iloc[-1]
            improvement = (
                np.nan
                if rank_start == 0
                else (rank_start - rank_end) / rank_start * 100
            )
            rows.append(
                {
                    "player_name": player,
                    "nextgen_win_rate": nextgen["win"].mean(),
                    "nextgen_improvement": improvement,
                    "senior_win_rate": senior["win"].mean(),
                }
            )

    players = pd.DataFrame(rows)
    winrate_r, winrate_p = stats.pearsonr(
        players["nextgen_win_rate"], players["senior_win_rate"]
    )
    imp = players.dropna(subset=["nextgen_improvement"])
    improvement_r, improvement_p = stats.pearsonr(
        imp["nextgen_improvement"], imp["senior_win_rate"]
    )

    return {
        "n_players": len(players),
        "winrate_r": round(winrate_r, 3),
        "winrate_p": winrate_p,
        "improvement_r": round(improvement_r, 3),
        "improvement_p": improvement_p,
        "players": players,
    }