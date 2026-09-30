"""Walk-forward backtest against the closing line.

For each (season, week), in chronological order: fit the model on every
game played before that week, predict the week's games, and bet where the
model disagrees with the closing line by at least `threshold` points.

Two numbers matter:
- CLV (closing line value): mean points of disagreement per bet. Positive
  means the model systematically prices games differently than the market.
  Necessary but not sufficient: a model can have CLV and still lose if its
  disagreements point the wrong way.
- ROI at -110 flat stakes: the only number that pays. Pushes refund.

No lookahead: the model never sees the target week or anything after it.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import models

RISK = 1.10  # risk $1.10 to win $1.00
PAYOUT = 1.00


@dataclass
class Bet:
    season: int
    week: int
    away: str
    home: str
    side: str  # "home" or "away"
    line: float
    model_margin: float
    edge_pts: float
    margin: float
    result: str  # "win", "loss", "push"


@dataclass
class Report:
    bets: list[Bet]
    threshold: float

    @property
    def n(self) -> int:
        return len(self.bets)

    @property
    def decided(self) -> list[Bet]:
        return [b for b in self.bets if b.result != "push"]

    @property
    def wins(self) -> int:
        return sum(1 for b in self.decided if b.result == "win")

    @property
    def clv(self) -> float:
        return sum(b.edge_pts for b in self.bets) / self.n if self.n else 0.0

    @property
    def roi(self) -> float:
        d = self.decided
        if not d:
            return 0.0
        profit = self.wins * PAYOUT - (len(d) - self.wins) * RISK
        return profit / (len(d) * RISK)


def run(games: pd.DataFrame, model_name: str = "power", threshold: float = 2.0) -> Report:
    bets: list[Bet] = []
    weeks = games[["season", "week"]].drop_duplicates().sort_values(["season", "week"])
    for season, week in weeks.itertuples(index=False):
        train = games[(games["season"] < season) | ((games["season"] == season) & (games["week"] < week))]
        today = games[(games["season"] == season) & (games["week"] == week)]
        if model_name == "power":
            model = models.PowerRating().fit(train)
        else:
            raise ValueError(f"unknown model {model_name}")
        for _, g in today.iterrows():
            m = model.predict(g["away_team"], g["home_team"])
            if m is None:
                continue
            line = float(g["spread_line"])
            edge = abs(m - line)
            if edge < threshold:
                continue
            side = "home" if m > line else "away"
            margin = float(g["home_margin"])
            if side == "home":
                result = "win" if margin > line else ("push" if margin == line else "loss")
            else:
                result = "win" if margin < line else ("push" if margin == line else "loss")
            bets.append(Bet(season, int(week), g["away_team"], g["home_team"],
                            side, line, m, edge, margin, result))
    return Report(bets, threshold)
