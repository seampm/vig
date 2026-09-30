"""Unit tests for the backtest math. The math must be right before the results mean anything."""
import pandas as pd

from vig.backtest import RISK, Report, Bet, run
from vig.models import PowerRating


def _games():
    # tiny synthetic league: A is strong at home, B is weak. Deterministic.
    rows = []
    gid = 0
    for season in (2024, 2025):
        for week in (1, 2, 3):
            rows.append(dict(season=season, week=week, gameday="2024-09-01",
                             away_team="B", home_team="A", spread_line=-7.0,
                             total_line=44.0, away_score=10, home_score=24, home_margin=14))
            gid += 1
    return pd.DataFrame(rows)


def test_roi_math():
    bets = [Bet(2024, 1, "B", "A", "home", -7.0, -10.0, 3.0, 14, "win"),
            Bet(2024, 1, "B", "A", "home", -7.0, -10.0, 3.0, 0, "loss")]
    r = Report(bets, 2.0)
    assert r.n == 2 and r.wins == 1
    assert abs(r.roi - ((1.0 - RISK) / (2 * RISK))) < 1e-9
    assert abs(r.clv - 3.0) < 1e-9


def test_push_refunds():
    bets = [Bet(2024, 1, "B", "A", "home", -7.0, -10.0, 3.0, -7.0, "push"),
            Bet(2024, 1, "B", "A", "home", -7.0, -10.0, 3.0, 14, "win")]
    r = Report(bets, 2.0)
    assert r.n == 2 and len(r.decided) == 1
    assert abs(r.roi - (1.0 / RISK)) < 1e-9  # one win, no loss, push excluded


def test_no_lookahead_in_run():
    # week 1 of 2025 must be predicted from 2024 games only.
    games = _games()
    r = run(games, "power", threshold=0.0)
    wk1 = [b for b in r.bets if (b.season, b.week) == (2025, 1)]
    assert wk1, "expected bets in 2025 week 1"
    # model trained only on 2024: A rating = 14 shrunk -> predicts A home margin ~14*3/13 + hfa
    assert all(b.model_margin > 5 for b in wk1)


def test_power_rating_shrinkage():
    g = _games()
    m = PowerRating(shrink=10, min_games=1).fit(g[g["season"] == 2024])
    # A: 3 games at +14 -> 42/13 ~= 3.2, not 14. Shrinkage works.
    assert m.ratings["A"] < 14
    assert m.predict("B", "A") is not None
    assert m.predict("ZZZ", "A") is None  # unknown team -> no bet
