# Decisions

The lab notebook. Every consequential choice gets an entry: what was decided, why, and what the alternatives were. AI forgets; this file doesn't.

## ADR-001: Why this project (2026-09-30)

AI can scaffold an app in an afternoon, but scaffolds don't survive contact with reality. The failure mode is always the same: wide and shallow, nobody owns the vision, and month two is when changes get scary because nobody understands the thing deeply.

So this project is designed against that failure:

- **A real question, not a demo.** "Can you beat the closing line?" has a right answer and real stakes. It can inform actual bets and fantasy decisions.
- **A month of depth, not a day of breadth.** The day-1 model is deliberately naive. Every day after that is one hypothesis tested honestly.
- **Built for daily contribution.** Small surface, fast backtest (~10s), one new idea per day.
- **Not a tiny-demo.** No `tiny` prefix, no toy. The name is `vig`: the bookmaker's cut, the thing you have to beat.

## ADR-002: How AI fits (2026-09-30)

The honest division of labor, learned the hard way:

- **Peter owns**: the hypotheses, the modeling choices, whether a result is real or overfit, and what to build next. These are judgment calls. AI has no taste and no stakes, so it cannot make them.
- **AI does**: implementation, data plumbing, test harnesses, boilerplate, running experiments, and writing up results. The world's fastest junior engineer.
- **The contract**: Peter writes the hypothesis before AI runs anything. Every experiment gets an entry here, including the ones that lose money. Especially those.

## ADR-003: Data (2026-09-30)

nflverse publishes every game with closing spread/total lines, moneylines, and final scores (`games.parquet` under the `schedules` release). Real market data, free, no scraping, no API keys. Verified: 1,663 played regular-season games 2020-2026, zero missing spread lines.

Convention (verified empirically, not assumed): `spread_line` is the AWAY team's line. A home bet wins iff `home_margin > spread_line`. The check: when `spread_line < 0` (away favored), home wins 33%; when positive, home wins 67%.

## ADR-004: The evaluation (2026-09-30)

- Walk-forward only. For each week, the model trains on strictly earlier games. No lookahead, ever.
- The market is the null hypothesis. The closing line is itself a model; everything is measured against it.
- Two metrics: CLV (avg points of disagreement per bet — necessary but not sufficient) and ROI at -110 flat stakes (the only number that pays; pushes refund).
- Thresholds are reported, not tuned. The day-1 table shows 1.0/2.0/3.0 with no selection.

## ADR-005: Day-1 baseline (2026-09-30)

Shrunk point-differential power rating (shrink=10, min 3 games, HFA estimated from the training window):

```
thresh  bets    CLV   win%     ROI
1.0     1378   4.61  50.1%   -4.3%
2.0     1144   5.26  50.2%   -4.1%
3.0      880   6.09  51.5%   -1.7%
```

Interpretation: high CLV, no profit. The rating disagrees with the market constantly (83% of games at threshold 1.0) and the disagreements are noise. Losing 4.3% is losing exactly the vig, which means the model is a random bettor with opinions. The market prices in everything a raw point differential knows, plus injuries, rest, and weather, which it doesn't.

Candidate directions (hypotheses for future days, not conclusions):
- EPA-based ratings instead of raw points (points are noisy; efficiency is stickier).
- Rest and travel adjustments (the market may underprice short rest).
- Totals instead of spreads (different market, possibly softer).
- Shrinkage tuning is NOT on the list: tuning constants on the backtest is how you manufacture fake edge.
