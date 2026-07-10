"""Tests for src.analysis — hand-built fixtures plus real-data checks."""

import pandas as pd
import pytest

from src.analysis import assign_rank_group, win_rate_by_group, upset_rate_by_group
from src.data_loader import load_matches


@pytest.fixture
def tiny_df():
    """Six matches with hand-computable outcomes."""
    return pd.DataFrame({
        "player_name": ["A", "A", "A", "B", "B", "B"],
        "player_rank": [10, 10, 10, 150, 150, 150],
        "rank_diff": [-5, -5, 5, -20, 30, 30],
        "win": [1, 1, 0, 0, 1, 0],
    })


@pytest.fixture(scope="module")
def real_df():
    """The actual dataset — loaded once for the whole module."""
    return load_matches()


class TestAssignRankGroup:
    def test_boundaries(self, tiny_df):
        df = pd.DataFrame({"player_rank": [1, 20, 21, 100, 101, 200, 201]})
        out = assign_rank_group(df)
        assert list(out["rank_group"]) == [
            "Elite (Top 20)", "Elite (Top 20)",
            "Tour Regular (21-100)", "Tour Regular (21-100)",
            "Challenger (101-200)", "Challenger (101-200)",
            "Qualifier (200+)",
        ]

    def test_does_not_mutate_input(self, tiny_df):
        before = tiny_df.copy()
        assign_rank_group(tiny_df)
        pd.testing.assert_frame_equal(tiny_df, before)


class TestWinRateByGroup:
    def test_hand_computed(self, tiny_df):
        out = win_rate_by_group(assign_rank_group(tiny_df), "rank_group")
        elite = out[out["rank_group"] == "Elite (Top 20)"].iloc[0]
        # Player A (rank 10): 2 wins in 3 matches
        assert elite["total_matches"] == 3
        assert elite["win_pct"] == pytest.approx(66.67, abs=0.01)

    def test_reproduces_published_figures(self, real_df):
        """Regression test: the README's rank-group win rates."""
        out = win_rate_by_group(assign_rank_group(real_df), "rank_group")
        assert list(out["win_pct"]) == [67.98, 47.62, 41.91, 33.11]


class TestUpsetRate:
    def test_only_favourites_counted(self, tiny_df):
        out = upset_rate_by_group(assign_rank_group(tiny_df))
        # rank_diff < 0 rows: A twice (both wins), B once (a loss) -> 1 upset
        assert out["times_favourite"].sum() == 3
        assert out["times_upset"].sum() == 1