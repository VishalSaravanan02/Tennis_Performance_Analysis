"""
Central configuration for the Tennis Performance Analysis project.

Every constant used across the analysis notebooks, dashboard and tests
lives here, so a value is only ever defined once.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# config.py sits in src/, so two .parent hops reach the repo root.
# Resolved from the file itself so imports work from notebooks, app or tests.
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_FILE = DATA_DIR / "processed" / "matches_cleaned.csv"
MODELS_DIR = ROOT_DIR / "models"
MODEL_FILE = MODELS_DIR / "match_predictor.pkl"

# ---------------------------------------------------------------------------
# Rank groups
# Final grouping from notebooks/01_ranking_performance — chosen after
# exploring the player rank distribution (initial 6-bin split was collapsed
# to 4 groups with sufficient sample sizes).
# ---------------------------------------------------------------------------
RANK_GROUP_BINS = [0, 20, 100, 200, 2000]
RANK_GROUP_LABELS = [
    "Elite (Top 20)",
    "Tour Regular (21-100)",
    "Challenger (101-200)",
    "Qualifier (200+)",
]

# ---------------------------------------------------------------------------
# Points gap groups
# From notebooks/01 — bins the rank-points difference between player and
# opponent to show how win rate scales with quality gap magnitude.
# ---------------------------------------------------------------------------
POINTS_GAP_BINS = [-20000, -3000, -1000, -500, 0, 500, 1000, 3000, 20000]
POINTS_GAP_LABELS = [
    "Massive deficit",
    "Large deficit",
    "Moderate deficit",
    "Slight deficit",
    "Slight advantage",
    "Moderate advantage",
    "Large advantage",
    "Massive advantage",
]

# ---------------------------------------------------------------------------
# Career stages
# From notebooks/03_junior_pathway — each match classified by the player's
# age at the time of the match. Labels must match the notebook exactly so
# dashboard output is consistent with saved figures.
# ---------------------------------------------------------------------------
JUNIOR_MAX_AGE = 18   # age <= 18            -> Junior (U18)
NEXTGEN_MAX_AGE = 21  # 18 < age <= 21       -> Next Gen (19-21)
                      # age > 21             -> Senior (21+)
STAGE_JUNIOR = "Junior (U18)"
STAGE_NEXTGEN = "Next Gen (19-21)"
STAGE_SENIOR = "Senior (21+)"
STAGE_ORDER = [STAGE_JUNIOR, STAGE_NEXTGEN, STAGE_SENIOR]

# ---------------------------------------------------------------------------
# Analysis thresholds
# From notebooks/03 — minimum matches a player needs in a career stage for
# slope/volatility/transition metrics to be meaningful. This is the
# threshold behind the n=24 Next Gen -> Senior correlation finding.
# ---------------------------------------------------------------------------
MIN_MATCHES_PER_STAGE = 3

# ---------------------------------------------------------------------------
# Competitive density groups
# From notebooks/05_health_fatigue — buckets of match_load_7 (matches played
# in the prior 7 days, tournament-date proxy).
# ---------------------------------------------------------------------------
DENSITY_FRESH = "0 — Fresh"
DENSITY_LOW = "1-2 — Low"
DENSITY_MEDIUM = "3-4 — Medium"
DENSITY_HIGH = "5-6 — High"
DENSITY_VERY_HIGH = "7+ — Very High"
DENSITY_ORDER = [
    DENSITY_FRESH, DENSITY_LOW, DENSITY_MEDIUM, DENSITY_HIGH, DENSITY_VERY_HIGH,
]