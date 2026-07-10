"""
Competitive load and fatigue analysis functions.

Extracted from notebooks/05_health_fatigue. Bins 7-day match load into
density groups and analyses the relationship between competitive density
and performance, including the rank-group interaction.
"""

import numpy as np
import pandas as pd
from scipy.stats import f_oneway

from src.config import DENSITY_ORDER, RANK_GROUP_LABELS


def assign_density_group(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a 'density_group_7' column from match_load_7."""
    out = df.copy()
    load = out["match_load_7"]
    conditions = [load == 0, load <= 2, load <= 4, load <= 6]
    out["density_group_7"] = np.select(
        conditions, DENSITY_ORDER[:4], default=DENSITY_ORDER[4]
    )
    return out


def win_rate_by_density(df: pd.DataFrame) -> pd.DataFrame:
    """
    Win rate per competitive density group, averaged at the player level.

    Per-player win rates are computed within each density group first,
    then averaged across players, so high-volume players do not dominate
    (see notebooks/05).

    Returns: density_group_7, avg_win_rate (%), players — ordered by
    DENSITY_ORDER.
    """
    per_player = (
        df.groupby(["player_name", "density_group_7"])["win"].mean().reset_index()
    )
    result = (
        per_player.groupby("density_group_7")
        .agg(avg_win_rate=("win", "mean"), players=("win", "count"))
        .reindex(DENSITY_ORDER)
        .reset_index()
    )
    result["avg_win_rate"] = (result["avg_win_rate"] * 100).round(2)
    return result


def density_anova(df: pd.DataFrame) -> dict:
    """
    One-way ANOVA: do match-level win outcomes differ across density groups?

    Returns a dict with f_stat and p_value.
    """
    groups = [
        df[df["density_group_7"] == group]["win"].values
        for group in DENSITY_ORDER
    ]
    f_stat, p_value = f_oneway(*groups)
    return {"f_stat": round(f_stat, 4), "p_value": p_value}


def density_rank_interaction(df: pd.DataFrame, min_matches: int = 20) -> dict:
    """
    Win rate matrix: rank group x competitive density (match-level means).

    Cells with fewer than min_matches matches are unreliable; the returned
    mask marks them (see the hatched cells in the notebook heatmap).

    Requires both 'rank_group' and 'density_group_7' columns — apply
    analysis.assign_rank_group and assign_density_group first.

    Returns a dict with:
        win_matrix   — win rate (%) per rank group x density group
        count_matrix — match counts per cell
        mask         — True where count < min_matches
    """
    grouped = (
        df.groupby(["rank_group", "density_group_7"], observed=True)["win"]
        .agg(win_rate="mean", matches="count")
        .reset_index()
    )
    grouped["win_rate"] = (grouped["win_rate"] * 100).round(2)

    win_matrix = (
        grouped.pivot(index="rank_group", columns="density_group_7", values="win_rate")
        .reindex(index=RANK_GROUP_LABELS, columns=DENSITY_ORDER)
    )
    count_matrix = (
        grouped.pivot(index="rank_group", columns="density_group_7", values="matches")
        .reindex(index=RANK_GROUP_LABELS, columns=DENSITY_ORDER)
    )
    return {
        "win_matrix": win_matrix,
        "count_matrix": count_matrix,
        "mask": count_matrix < min_matches,
    }