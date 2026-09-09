# Research Note

## Research question

Can an absolute-return equity portfolio keep market-neutral stock selection and
directional risk management separately governed—and can P&L attribution reveal
which sleeve drove the result?

## Decisions that shaped the research

### 1. Make the information clock explicit

Each observation has a decision time, an execution time, and a return interval.
Information observed after the close first affects the next eligible open. For
walk-forward evaluation, training ends early enough that no unresolved label
overlaps the test window.

This converts “no look-ahead” from an intention into a checkable contract. The
public implementation of that contract is in
[`contracts.py`](public_reference/contracts.py).

### 2. Build a market-neutral stock-selection core

The Alpha Core translates cross-sectional scores into long and short positions,
then evaluates dollar, sector, and estimated beta exposure. Its job is to express
relative stock selection without relying on a directional market forecast.

The public reference code focuses on the invariants around this step rather
than disclosing the feature set, model, optimizer, or thresholds.

### 3. Govern directional risk as a separate sleeve

Market trend, realized volatility, and VIX govern a separate Directional Risk
Overlay. When active, the overlay adds exposure across names already selected
for the Alpha Core long book; it does not rerank the cross-section.

This distinction matters. The overlay is not a pure market-beta instrument, so
the two sleeves support decision-level attribution, not a claim that portfolio
returns have been cleanly decomposed into statistical alpha and beta.

### 4. Reconcile decisions into portfolio P&L

The accounting layer starts from prior weights, applies next-open-to-next-open
returns, charges one-way turnover costs, and verifies that sleeve contributions
reconcile exactly to total gross P&L before costs. This keeps exposure,
turnover, cost sensitivity, drawdown, and attribution connected to the same
portfolio decisions.

### 5. Preserve the holdout interpretation

The research design was fixed before a one-time 76-session holdout. The combined
portfolio met its criteria, but sleeve-level attribution showed that the Alpha
Core detracted while the Directional Risk Overlay drove the gain. That result
does not erase the portfolio outcome; it makes the next research question more
specific.

## Architecture in code

The repository includes a small executable reference built on synthetic inputs:

```text
ResearchPanel + DecisionClock + WalkForwardSplit
  -> protected scoring and portfolio-construction interfaces
  -> Alpha Core weights and exposure checks
  -> Directional Risk Overlay weights
  -> next-open returns
  -> turnover, transaction cost, and sleeve-level P&L reconciliation
  -> cross-layer audit record
```

Start with [`walkthrough.py`](public_reference/walkthrough.py), then follow the
modules in [`public_reference/`](public_reference/). The code is deliberately
organized by research contract and covered by tests for the conditions most
likely to invalidate a backtest. The full stage-by-stage design is documented
in [System Design](docs/SYSTEM_DESIGN.md).

## What changed after research review

The final presentation makes four choices explicit: the information clock,
purged walk-forward separation, separate governance of the two portfolio
sleeves, and exact P&L reconciliation. It also retains the fixed-universe and
market-friction limitations alongside the results.
