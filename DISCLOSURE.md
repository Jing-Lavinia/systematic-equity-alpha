# Public Research Boundary

This repository presents the reasoning, portfolio architecture, reviewed
evidence, and limitations of a private quantitative research project.

## Included

- the research question and information-clock contract;
- the end-to-end system design and research decision chain;
- portfolio-layer definitions and exposure checks;
- reviewed development, robustness, cost-sensitivity, and holdout evidence;
- sleeve-level P&L attribution and interpretation boundaries;
- executable reference code using synthetic inputs.

## Not included

- source data or vendor-specific data preparation;
- feature definitions and transformations;
- fitted models, parameters, thresholds, or serialized artifacts;
- the production portfolio optimizer and operational infrastructure;
- private research notebooks and full experiment history.

The code in [`public_reference/`](public_reference/) implements the
architecture’s key contracts on synthetic inputs. It is not a redacted copy of
the private strategy and did not produce the reported results.

All performance figures are simulated and are not investment advice.
