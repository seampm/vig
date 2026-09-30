"""Game lines and scores from nflverse.

nflverse publishes every game with its closing spread/total lines and the
final score. That is real market data, free, no scraping needed. The whole
project stands on this file: if the data is wrong here, every result after
it is fiction.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE_URL = "https://github.com/nflverse/nflverse-data/releases/download"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _download() -> Path:
    path = DATA_DIR / "games.parquet"
    if path.exists():
        return path
    import requests

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_URL}/schedules/games.parquet"
    resp = requests.get(url, timeout=600, allow_redirects=True)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return path


def load_games(first_season: int = 2020) -> pd.DataFrame:
    """Played regular-season games with closing lines, oldest first.

    Columns: season, week, gameday, away_team, home_team, spread_line,
    total_line, away_score, home_score, home_margin.

    Convention (verified against 2020-2025 results): spread_line is the AWAY
    team's line. A bet on the home team wins iff home_margin > spread_line.
    """
    df = pd.read_parquet(_download())
    g = df[
        (df["season"] >= first_season)
        & (df["game_type"] == "REG")
        & df["away_score"].notna()
        & df["spread_line"].notna()
    ].copy()
    g["home_margin"] = g["home_score"] - g["away_score"]
    keep = [
        "season", "week", "gameday", "away_team", "home_team",
        "spread_line", "total_line", "away_score", "home_score", "home_margin",
    ]
    return g[keep].sort_values(["season", "week", "gameday"]).reset_index(drop=True)
