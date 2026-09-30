"""Forecasting models. Every model predicts home_margin (home_score - away_score)
for a game, using only games played before that game's week.

The null model is the market itself: predicted margin = spread_line. You
cannot beat it by definition, which is the point. Every other model has to
earn its existence against that baseline.
"""
from __future__ import annotations

import pandas as pd


def market(game: pd.Series) -> float:
    """The efficient-market null: the closing line is the forecast."""
    return float(game["spread_line"])


class PowerRating:
    """Shrunk point-differential ratings, refit walk-forward.

    rating(team) = sum(point diffs) / (games + k): early-season ratings stay
    near zero instead of exploding on one blowout. Home-field advantage is
    estimated from the training window itself, not assumed.
    """

    def __init__(self, shrink: int = 10, min_games: int = 3):
        self.shrink = shrink
        self.min_games = min_games
        self.ratings: dict[str, float] = {}
        self.hfa: float = 0.0
        self._counts: dict[str, int] = {}

    def fit(self, games: pd.DataFrame) -> "PowerRating":
        diffs: dict[str, float] = {}
        counts: dict[str, int] = {}
        for _, g in games.iterrows():
            m = float(g["home_margin"])
            for team, d in ((g["home_team"], m), (g["away_team"], -m)):
                diffs[team] = diffs.get(team, 0.0) + d
                counts[team] = counts.get(team, 0) + 1
        self.ratings = {t: diffs[t] / (counts[t] + self.shrink) for t in diffs}
        self._counts = counts
        self.hfa = float(games["home_margin"].mean()) if len(games) else 0.0
        return self

    def predict(self, away_team: str, home_team: str) -> float | None:
        """Predicted home margin, or None if either team lacks history."""
        if self._counts.get(away_team, 0) < self.min_games:
            return None
        if self._counts.get(home_team, 0) < self.min_games:
            return None
        return self.ratings[home_team] - self.ratings[away_team] + self.hfa
