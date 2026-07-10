"""Tests for src.pathway — career stages and the headline n=24 finding."""

import pandas as pd
import pytest

from src.data_loader import load_matches
from src.pathway import assign_career_stage, nextgen_senior_correlation


@pytest.fixture(scope="module")
def real_df():
    return assign_career_stage(load_matches())


class TestAssignCareerStage:
    def test_boundaries(self):
        df = pd.DataFrame({"player_age": [16.0, 18.0, 18.1, 21.0, 21.1, 30.0]})
        out = assign_career_stage(df)
        assert list(out["career_stage"]) == [
            "Junior (U18)", "Junior (U18)",
            "Next Gen (19-21)", "Next Gen (19-21)",
            "Senior (21+)", "Senior (21+)",
        ]


class TestHeadlineFinding:
    """Regression tests: the README's junior pathway claims."""

    def test_n_players_is_24(self, real_df):
        assert nextgen_senior_correlation(real_df)["n_players"] == 24

    def test_consistency_correlation(self, real_df):
        result = nextgen_senior_correlation(real_df)
        assert result["winrate_r"] == pytest.approx(0.718, abs=0.001)
        assert result["winrate_p"] < 0.001

    def test_improvement_does_not_predict(self, real_df):
        result = nextgen_senior_correlation(real_df)
        assert result["improvement_r"] == pytest.approx(0.130, abs=0.001)
        assert result["improvement_p"] > 0.05

    def test_robust_to_threshold(self, real_df):
        """The slider discovery, pinned: correlation holds at a stricter cut."""
        result = nextgen_senior_correlation(real_df, min_matches=10)
        assert result["winrate_r"] > 0.6