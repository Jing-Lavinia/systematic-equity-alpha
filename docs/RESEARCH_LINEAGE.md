# Research Lineage

This page shows how the final specification became reviewable. It is organized
around decisions and evidence rather than a chronological experiment diary.

## Decision chain

| Checkpoint | Question | Decision retained in the final design | Evidence or invariant |
|---|---|---|---|
| Information timing | When can each input first affect a trade? | Close-time information first enters next-open weights | `information_time < execution_time < pnl_end_time` |
| Executable label | Does the prediction target match a tradable interval? | Forward labels begin at open `t+1` | Target and portfolio P&L share the same execution anchor |
| Walk-forward separation | Can an unresolved label cross the test boundary? | Rolling training with an effective 11-session purge | Overlapping splits are rejected |
| Tail modelling | Are winners and losers symmetric prediction problems? | Upper and lower tails are classified separately | Two score streams feed one cross-sectional ranking |
| Neutral stock selection | Is the ranking relying on broad market exposure? | Build a dollar-, sector-, and estimated-beta-controlled Alpha Core | Exposure checks run before the overlay |
| Directional risk | Should market state alter stock selection? | Keep ranking fixed and govern net exposure in a separate sleeve | Overlay only uses names in the Alpha Core long book |
| Execution realism | Are turnover and timing connected to realized positions? | Next-open simulation with one-way turnover costs | Prior weights, target weights, and returns share one interval |
| Attribution | Which decision created the portfolio result? | Reconcile Alpha Core, overlay, and transaction costs every period | Sleeve sum equals total P&L |
| Final evaluation | Was later data reused for model selection? | Fix the research design before one one-time holdout | Holdout result and adverse component attribution are both retained |

## Robustness map

Robustness checks were used to ask whether the development result depended on a
single convenient specification. They reduce selection risk; they do not turn
simulated performance into a guarantee.

| Dimension varied | Reviewed outcome |
|---|---|
| One-way transaction cost | Sharpe remained 1.16 at 20 bps |
| Nearby parameter grid | All nine configurations were profitable |
| Deterministic 80% stock subsets | Ten subsets; minimum CAGR 20.55%, minimum Sharpe 1.095 |
| Single-sector exclusions | Every exclusion remained profitable |
| Random seed | Seeds 7, 42, and 137 met the point-estimate criteria |
| Training window | 1.0, 1.5, and 2.0 years met the point-estimate criteria |
| Multiple-testing adjustment | Deflated Sharpe probability estimate 90.64% across ten recorded trials |
| Block bootstrap | 2.5th percentile: 10.10% CAGR and -31.24% drawdown |

The bootstrap tail is intentionally different from a point estimate: it shows
that parameter stability and path uncertainty answer different questions.

## Development to holdout interpretation

```text
development portfolio
  -> 23.49% CAGR · 1.24 Sharpe · -16.10% maximum drawdown at 5 bps
  -> specification fixed
  -> one-time 76-session holdout
  -> +7.71% · 1.39 annualized Sharpe · -8.23% maximum drawdown
  -> Alpha Core -1.58% gross · Directional Risk Overlay +9.68% gross
  -> next question: is the Alpha Core independently stable on genuinely new data?
```

The holdout therefore adds information in two directions. It supports the
combined portfolio result over that short window, while narrowing the claim
that can be made about the stock-selection sleeve on its own.

## Repository evidence map

- The README gives the result and the main interpretation.
- [System design](SYSTEM_DESIGN.md) shows how data, model, portfolio, execution,
  and evidence layers depend on one another.
- [`public_reference/`](../public_reference/) implements the cross-layer
  contracts on synthetic inputs.
- [`tests/`](../tests/) shows which failures the public architecture is designed
  to catch.
- [Evidence and limitations](../EVIDENCE_AND_LIMITATIONS.md) separates reviewed
  facts from the claims they do not support.
