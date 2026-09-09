# Public Reference Code

This package is an executable map of the project architecture. It uses only
Python's standard library and synthetic inputs. The aim is to expose the
research contracts and control flow without publishing the private strategy.

## Reading order

1. [`walkthrough.py`](walkthrough.py) connects a synthetic information set to
   scores, two portfolio sleeves, next-open P&L, and an audit record.
2. [`data_contracts.py`](data_contracts.py) checks cross-sectional schema,
   uniqueness, feature values, and information timestamps.
3. [`contracts.py`](contracts.py) makes execution timing and label purge
   assumptions testable.
4. [`research_pipeline.py`](research_pipeline.py) sequences the full decision
   while injecting the protected model, optimizer, and overlay policy.
5. [`portfolio_layers.py`](portfolio_layers.py) checks the Alpha Core and adds a
   separately governed Directional Risk Overlay.
6. [`accounting.py`](accounting.py) reconciles sleeve-level P&L, turnover, and
   transaction costs.
7. [`audit.py`](audit.py) combines timing, data shape, exposures, and accounting
   into one review record.
8. [`../tests/`](../tests/) exercises data, timing, pipeline, portfolio, and
   accounting failure conditions as well as the intended path.

## Boundary map

```text
public and executable                     private implementation
──────────────────────────────────────    ───────────────────────────────
cross-sectional data contracts            vendor-specific ingestion
information clock and purge checks        exact feature transformations
pipeline sequencing and interfaces        fitted model and artifacts
neutrality and composition checks         production portfolio optimizer
turnover, cost, and P&L reconciliation    live thresholds and run history
```

The three injected interfaces in `research_pipeline.py` make the boundary
explicit. The public pipeline still validates their outputs, so private logic
cannot silently bypass timing, cross-sectional coverage, or portfolio controls.

## Run

From the repository root:

```bash
python -m public_reference.walkthrough
python -m unittest discover -s tests -v
```

The walkthrough uses a four-security toy cross-section so every calculation is
easy to inspect. It is not a miniature version of the real alpha model and did
not generate the reported performance.
