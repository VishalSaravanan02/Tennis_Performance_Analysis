"""
Data loading and validation for the Tennis Performance Analysis project.

Provides a single entry point, load_matches(), used by the notebooks,
dashboard and tests. Validation runs on every load so that downstream
code can trust the dataframe's structure.
"""

import pandas as pd

from src.config import DATA_FILE

# Columns the analysis depends on. Validation fails loudly if any are absent.
REQUIRED_COLUMNS = [
    "tourney_name", "tourney_date", "tourney_level", "surface",
    "draw_size", "round", "best_of", "minutes", "score",
    "player_name", "player_rank", "player_rank_points", "player_age",
    "opponent_rank", "opponent_rank_points", "win", "rank_diff",
    "match_load_7", "match_load_14", "fatigue_score_7", "fatigue_score_14",
]

# Columns that must contain no missing values for the analysis to be valid.
KEY_COLUMNS = [
    "tourney_date", "player_name", "player_rank", "opponent_rank",
    "player_age", "win", "rank_diff", "surface", "round",
]


def validate_matches(df: pd.DataFrame) -> None:
    """
    Validate the structure and integrity of the matches dataframe.

    Raises:
        ValueError: if required columns are missing, the target column
            contains values other than 0/1, or key columns contain nulls.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Matches data is missing required columns: {missing}. "
            f"Expected the output of notebooks/00_data_cleaning.ipynb."
        )

    invalid_targets = set(df["win"].unique()) - {0, 1}
    if invalid_targets:
        raise ValueError(
            f"Column 'win' must contain only 0 and 1, "
            f"found unexpected values: {sorted(invalid_targets)}."
        )

    null_counts = df[KEY_COLUMNS].isnull().sum()
    nulls = null_counts[null_counts > 0]
    if not nulls.empty:
        raise ValueError(
            f"Null values found in key columns: {nulls.to_dict()}. "
            f"The cleaned dataset should contain no missing values."
        )


def load_matches(filepath=DATA_FILE) -> pd.DataFrame:
    """
    Load and validate the cleaned ATP matches dataset.

    Args:
        filepath: Path to the cleaned CSV. Defaults to the project's
            processed data file; tests can pass a different path.

    Returns:
        Validated matches dataframe with tourney_date parsed as datetime.

    Raises:
        FileNotFoundError: if the CSV does not exist.
        ValueError: if the data fails structural validation.
    """
    if not pd.io.common.file_exists(str(filepath)):
        raise FileNotFoundError(
            f"Cleaned data not found at {filepath}. "
            f"Run notebooks/00_data_cleaning.ipynb to generate it."
        )

    df = pd.read_csv(filepath, parse_dates=["tourney_date"])
    validate_matches(df)
    return df