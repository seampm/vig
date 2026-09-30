"""vig: can you beat the closing line? Run with: python -m vig"""
from .backtest import run
from .data import load_games


def main() -> None:
    games = load_games()
    seasons = f"{int(games['season'].min())}-{int(games['season'].max())}"
    print(f"vig — walk-forward vs the closing NFL line ({seasons}, {len(games)} games)")
    print("Bet when the power rating disagrees with the line by >= threshold pts, -110 flat.\n")
    print(f"{'model':<12}{'thresh':>7}{'bets':>6}{'CLV':>7}{'win%':>7}{'ROI':>8}")
    for threshold in (1.0, 2.0, 3.0):
        r = run(games, "power", threshold)
        d = r.decided
        winpct = f"{100 * r.wins / len(d):.1f}%" if d else "n/a"
        print(f"{'power':<12}{threshold:>7.1f}{r.n:>6}{r.clv:>7.2f}{winpct:>7}{r.roi:>7.1%}")
    print("\nCLV = avg points of disagreement per bet. ROI is what pays.")
    print("The market is the null hypothesis: expect ~0 edge. Finding real")
    print("edge without fooling yourself is the entire project.")


if __name__ == "__main__":
    main()
