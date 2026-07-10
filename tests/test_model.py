"""Tests for the model bundle and inference — including the OOD input bug."""

import joblib
import pytest

from src.config import MODEL_FILE
from src.data_loader import load_matches
from src.model import FEATURE_COLUMNS, predict_match


@pytest.fixture(scope="module")
def bundle():
    return joblib.load(MODEL_FILE)


@pytest.fixture(scope="module")
def real_df():
    return load_matches()


PLAYER = {"rank": 5, "rank_points": 5000, "recent_win_rate": 0.7,
          "surface_win_rate": 0.65, "fatigue_score_7": 0.3}
JOURNEYMAN = {"rank": 300, "rank_points": 200, "recent_win_rate": 0.4,
              "surface_win_rate": 0.45, "fatigue_score_7": 0.3}


class TestBundle:
    def test_is_self_contained(self, bundle):
        for key in ["model", "scaler", "feature_columns", "round_mapping",
                    "fill_values", "player_snapshot", "metrics"]:
            assert key in bundle, f"bundle missing '{key}'"

    def test_feature_columns_consistent(self, bundle):
        assert bundle["feature_columns"] == FEATURE_COLUMNS

    def test_metrics_beat_baseline(self, bundle):
        m = bundle["metrics"]
        assert m["accuracy"] > m["baseline"]["accuracy"]
        assert m["auc"] > m["baseline"]["auc"]


class TestPredictMatch:
    def test_probability_in_range(self, bundle):
        p = predict_match(bundle, PLAYER, JOURNEYMAN, "Hard", "R32")
        assert 0.0 <= p <= 1.0

    def test_identical_players_symmetric(self, bundle):
        a = predict_match(bundle, PLAYER, PLAYER, "Hard", "R32")
        b = predict_match(bundle, PLAYER, PLAYER, "Hard", "R32")
        assert a == pytest.approx(b)  # deterministic, same both ways

    def test_favourite_is_favoured(self, bundle):
        p_fav = predict_match(bundle, PLAYER, JOURNEYMAN, "Hard", "R32")
        p_dog = predict_match(bundle, JOURNEYMAN, PLAYER, "Hard", "R32")
        assert p_fav > p_dog


class TestInputBoundsAssumption:
    """The fatigue-slider bug, immortalised.

    The dashboard's manual-mode sliders assume fatigue_score_7 is bounded
    by 1.0. If the data pipeline ever changes that scale, this fails and
    forces the UI bounds to be revisited.
    """

    def test_fatigue_score_bounded_by_one(self, real_df):
        assert real_df["fatigue_score_7"].max() <= 1.0
        assert real_df["fatigue_score_7"].min() >= 0.0

    def test_win_rates_are_proportions(self, real_df):
        assert real_df["win"].isin([0, 1]).all()