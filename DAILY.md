# The daily loop

Thirty to forty-five minutes a day. That's the whole commitment, and it's enough if it's every day.

## One day

1. **Write the hypothesis first** (2 sentences, in DECISIONS.md). Example: "EPA per play is stickier than raw point differential, so EPA-based ratings should disagree with the market less often but win more of those disagreements."
2. **Implement.** You direct, AI writes the code. You review the diff; if you can't explain what changed, it doesn't merge.
3. **Run** `python -m vig` and `pytest tests/`. Both must pass.
4. **Record the result** in DECISIONS.md: the numbers, what you think they mean, and what you'd try next. Losing results get the same care as winning ones. A losing experiment you understood is a contribution; a winning one you don't is a liability.

## What counts as a contribution

- A new model or a meaningful change to one
- A new data source, validated the way ADR-003 was
- A calibration or robustness check (does the edge survive by season? by week?)
- A writeup of a failed hypothesis with the reason you believe it failed

## What doesn't

- Tuning constants until the backtest looks good. That's manufacturing edge, and the ROI on unseen games will collect the debt.
- Adding features to the harness that don't serve a hypothesis. The harness is done until a hypothesis needs more from it.
- Big rewrites. Small diffs, every day, that you fully understand.

## The rule that matters

Never evaluate on the same games you used to choose the idea. Walk-forward is the floor. If an idea needs a separate holdout, say so in the hypothesis before running.
