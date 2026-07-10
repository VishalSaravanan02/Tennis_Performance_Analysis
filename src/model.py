"""
Match outcome prediction model.

Faithful port of notebooks/04_ml_match_prediction: feature engineering,
time-based train/test split (2022-23 / 2024), XGBoost final model, and a
self-contained artifact bundle so inference never recomputes or hardcodes
training-time parameters.
"""

from datetime import date

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

# Model-specific constants (live here, not config: they belong to this model)
FEATURE_COLUMNS = [
    "rank_diff", "points_gap",
    "surface_Hard", "surface_Clay", "surface_Grass",
    "recent_win_rate", "surface_win_rate",
    "round_encoded", "fatigue_score_7",
]
ROUND_MAPPING = {
    "R128": 1, "R64": 2, "R32": 3, "R16": 4,
    "QF": 5, "SF": 6, "F": 7,
    "RR": 3,  # round robin ~ R32
    "BR": 6,  # bronze match ~ SF
}
TRAIN_YEARS = [2022, 2023]
TEST_YEAR = 2024
RECENT_TOURNAMENTS = 3


def _recent_tournament_winrate(group: pd.DataFrame) -> pd.Series:
    """Win rate over a player's previous RECENT_TOURNAMENTS tournaments."""
    group = group.sort_values("tourney_date")
    win_rates = []
    for _, row in group.iterrows():
        previous = group[
            (group["tourney_date"] < row["tourney_date"])
            | (
                (group["tourney_date"] == row["tourney_date"])
                & (group["tourney_name"] != row["tourney_name"])
            )
        ]
        prev_tourneys = previous["tourney_name"].unique()[-RECENT_TOURNAMENTS:]
        prev_matches = previous[previous["tourney_name"].isin(prev_tourneys)]
        win_rates.append(
            np.nan if len(prev_matches) == 0 else prev_matches["win"].mean()
        )
    return pd.Series(win_rates, index=group.index)


def _surface_winrate(group: pd.DataFrame) -> pd.Series:
    """Time-aware win rate on the current match's surface (past matches only)."""
    group = group.sort_values("tourney_date")
    win_rates = []
    for _, row in group.iterrows():
        previous = group[
            (group["tourney_date"] < row["tourney_date"])
            & (group["surface"] == row["surface"])
        ]
        win_rates.append(
            np.nan if len(previous) == 0 else previous["win"].mean()
        )
    return pd.Series(win_rates, index=group.index)


def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Add all model features to a copy of df.

    Returns (engineered_df, fill_values) where fill_values records the
    constants used for NaN imputation — these travel in the model bundle
    so inference uses identical values.

    Note: fill constants are computed over the full dataframe, faithfully
    reproducing notebooks/04 (documented caveat: a strictly train-only
    fill is the more rigorous choice).
    """
    out = df.copy()
    out["year"] = out["tourney_date"].dt.year
    out["points_gap"] = out["player_rank_points"] - out["opponent_rank_points"]

    for surface in ["Hard", "Clay", "Grass"]:
        out[f"surface_{surface}"] = (out["surface"] == surface).astype(int)

    out["recent_win_rate"] = out.groupby("player_name", group_keys=False).apply(
        _recent_tournament_winrate, include_groups=False
    )
    out["surface_win_rate"] = out.groupby("player_name", group_keys=False).apply(
        _surface_winrate, include_groups=False
    )
    out["round_encoded"] = out["round"].map(ROUND_MAPPING).fillna(3)

    fill_values = {"recent_win_rate": out["win"].mean()}
    out["recent_win_rate"] = out["recent_win_rate"].fillna(
        fill_values["recent_win_rate"]
    )
    for surface in ["Hard", "Clay", "Grass"]:
        surface_mean = out[out["surface"] == surface]["win"].mean()
        fill_values[f"surface_win_rate_{surface}"] = surface_mean
        mask = out["surface_win_rate"].isna() & (out["surface"] == surface)
        out.loc[mask, "surface_win_rate"] = surface_mean

    return out, fill_values


def build_player_snapshot(engineered: pd.DataFrame) -> pd.DataFrame:
    """
    Latest per-player stats for inference: rank, points, recent form,
    fatigue, and full-history win rate per surface. Used by the dashboard's
    Match Predictor page so predictions use each player's current state.
    """
    latest = (
        engineered.sort_values("tourney_date")
        .groupby("player_name")
        .last()[["player_rank", "player_rank_points", "recent_win_rate",
                 "fatigue_score_7"]]
    )
    surface_wr = (
        engineered.groupby(["player_name", "surface"])["win"]
        .mean()
        .unstack()
        .rename(columns=lambda s: f"winrate_{s}")
    )
    return latest.join(surface_wr)


def train_model(engineered: pd.DataFrame) -> dict:
    """
    Train baseline + XGBoost on the time-based split and return the bundle.

    The bundle is self-contained: model, fitted scaler, feature columns,
    round mapping, fill values, player snapshot and evaluation metrics.
    """
    train = engineered[engineered["year"].isin(TRAIN_YEARS)]
    test = engineered[engineered["year"] == TEST_YEAR]

    X_train, y_train = train[FEATURE_COLUMNS], train["win"]
    X_test, y_test = test[FEATURE_COLUMNS], test["win"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Naive baseline: higher-ranked player wins
    baseline_preds = (X_test["rank_diff"] < 0).astype(int)
    baseline_preds[X_test["rank_diff"] == 0] = 1
    baseline = {
        "accuracy": accuracy_score(y_test, baseline_preds),
        "auc": roc_auc_score(y_test, -X_test["rank_diff"]),
    }

    model = xgb.XGBClassifier(
        n_estimators=100, random_state=42, eval_metric="logloss", verbosity=0
    )
    model.fit(X_train_scaled, y_train)
    probs = model.predict_proba(X_test_scaled)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, model.predict(X_test_scaled)),
        "auc": roc_auc_score(y_test, probs),
        "baseline": baseline,
        "train_rows": len(train),
        "test_rows": len(test),
    }

    return {
        "model": model,
        "scaler": scaler,
        "feature_columns": FEATURE_COLUMNS,
        "round_mapping": ROUND_MAPPING,
        "fill_values": None,  # set by caller (train_model.py) from engineer_features
        "player_snapshot": build_player_snapshot(engineered),
        "metrics": metrics,
        "train_years": TRAIN_YEARS,
        "test_year": TEST_YEAR,
        "trained_on": date.today().isoformat(),
    }


def predict_match(bundle: dict, p1_stats: dict, p2_stats: dict,
                  surface: str, round_name: str) -> float:
    """
    Win probability for player 1.

    p1_stats/p2_stats: dicts with rank, rank_points, recent_win_rate,
    surface_win_rate, fatigue_score_7 — from the bundle's player_snapshot
    or manual dashboard inputs.
    """
    row = pd.DataFrame([{
        "rank_diff": p1_stats["rank"] - p2_stats["rank"],
        "points_gap": p1_stats["rank_points"] - p2_stats["rank_points"],
        "surface_Hard": int(surface == "Hard"),
        "surface_Clay": int(surface == "Clay"),
        "surface_Grass": int(surface == "Grass"),
        "recent_win_rate": p1_stats["recent_win_rate"],
        "surface_win_rate": p1_stats["surface_win_rate"],
        "round_encoded": bundle["round_mapping"].get(round_name, 3),
        "fatigue_score_7": p1_stats["fatigue_score_7"],
    }])[bundle["feature_columns"]]
    scaled = bundle["scaler"].transform(row)
    return float(bundle["model"].predict_proba(scaled)[0, 1])