# vig

One honest question: can you beat the closing NFL line?

The line is the market's forecast. Bookmakers and thousands of bettors set it, and the vig means you need to win 52.4% of spread bets just to break even. This project builds forecasting models from scratch and tests them against that line, walk-forward, with no lookahead. If a model can't beat the close, it doesn't matter how clever it looks.

## Day 1 result

A shrunk point-differential power rating, bet whenever it disagrees with the closing line:

```
model        thresh  bets    CLV   win%     ROI
power           1.0  1378   4.61  50.1%   -4.3%
power           2.0  1144   5.26  50.2%   -4.1%
power           3.0   880   6.09  51.5%   -1.7%
```

Read it straight: the model disagrees with the market by 4-6 points a game and still loses at almost exactly the vig (-4.5%). Disagreeing with the market is not edge. The market is efficient against naive ratings. Everything from here is an attempt to find real signal without fooling yourself, which is the entire project.

## How it works

- `vig/data.py` — every played regular-season NFL game since 2020 with its closing spread/total and final score, from nflverse. Free, real market data.
- `vig/models.py` — forecasting models. Each predicts home margin using only games played before the target week. The null model is the market itself.
- `vig/backtest.py` — walk-forward backtest. Fit on the past, bet the current week where the model disagrees with the line, score CLV and ROI at -110 flat stakes. Pushes refund.
- `tests/` — the math is tested before the results are trusted.

```bash
pip install -r requirements.txt
python -m vig        # runs the backtest
pytest tests/        # 4 tests
```

## The daily loop

One hypothesis per day, written down before running anything. Implement it, run the backtest, record what happened in `DECISIONS.md`, win or lose. See `DAILY.md` for the contract.

## Decisions

`DECISIONS.md` is the lab notebook: why this project exists, how it's built, and what each day's experiment showed. Read it before contributing.
