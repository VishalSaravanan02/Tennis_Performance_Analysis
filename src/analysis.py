"""
Ranking and performance analysis functions.

Extracted from notebooks/01_ranking_performance and 02_player_progression.
All functions take a matches dataframe (as produced by data_loader.load_matches)
and return dataframes/Series — no printing, no plotting.
"""

import pandas as pd

from src.config import (
    RANK_GROUP_BINS,
    RANK_GROUP_LABELS,
    POINTS_GAP_BINS,
    POINTS_GAP_LABELS,
)


def assign_rank_group(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a categorical 'rank_group' column added."""
    out = df.copy()
    out["rank_group"] = pd.cut(
        out["player_rank"], bins=RANK_GROUP_BINS, labels=RANK_GROUP_LABELS
    )
    return out


def assign_points_gap_group(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with 'points_gap' and 'points_gap_group' columns added."""
    out = df.copy()
    out["points_gap"] = out["player_rank_points"] - out["opponent_rank_points"]
    out["points_gap_group"] = pd.cut(
        out["points_gap"], bins=POINTS_GAP_BINS, labels=POINTS_GAP_LABELS
    )
    return out


def win_rate_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Win rate and match counts per value of group_col.

    Returns a dataframe with columns: group_col, total_matches, wins, win_pct.
    """
    result = (
        df.groupby(group_col, observed=True)
        .agg(total_matches=("win", "count"), wins=("win", "sum"))
        .reset_index()
    )
    result["win_pct"] = (result["wins"] / result["total_matches"] * 100).round(2)
    return result


def upset_rate_by_group(df: pd.DataFrame, group_col: str = "rank_group") -> pd.DataFrame:
    """
    How often the favourite (higher-ranked player) loses, per group.

    Considers only matches with a clear favourite (rank_diff != 0), viewed
    from the favourite's perspective (rank_diff < 0 rows).

    Returns a dataframe with columns: group_col, times_favourite,
    times_upset, upset_rate (in %).
    """
    favourites = df[(df["rank_diff"] != 0) & (df["rank_diff"] < 0)]
    result = (
        favourites.groupby(group_col, observed=True)["win"]
        .agg(times_favourite="count", times_upset=lambda s: (s == 0).sum())
        .reset_index()
    )
    result["upset_rate"] = (
        result["times_upset"] / result["times_favourite"] * 100
    ).round(2)
    return result


def player_consistency(df: pd.DataFrame, min_matches: int = 3) -> pd.DataFrame:
    """
    Per-player win rate and volatility (std of win/loss outcomes).

    From notebooks/02 — higher volatility means less consistent results.
    Players with fewer than min_matches matches are excluded, as std is
    not meaningful on tiny samples.

    Returns a dataframe with columns: player_name, matches, win_rate, volatility.
    """
    result = (
        df.groupby("player_name")["win"]
        .agg(matches="count", win_rate="mean", volatility="std")
        .reset_index()
    )
    result = result[result["matches"] >= min_matches].dropna(subset=["volatility"])
    result["win_rate"] = result["win_rate"].round(4)
    result["volatility"] = result["volatility"].round(4)
    return result