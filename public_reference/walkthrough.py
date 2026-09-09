"""Run a synthetic end-to-end example of the public research architecture."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Mapping

from .accounting import attribute_one_period
from .audit import build_decision_audit
from .contracts import DecisionClock, WalkForwardSplit, eligible_training_end
from .data_contracts import FeatureRow, ResearchPanel
from .research_pipeline import DecisionInputs, ReferenceResearchPipeline


def _synthetic_scorer(panel: ResearchPanel) -> dict[str, float]:
    """Expose a supplied toy score; this is not a public strategy feature."""

    return {
        security: values["synthetic_score"]
        for security, values in panel.as_feature_matrix().items()
    }


def _synthetic_neutral_core(
    scores: Mapping[str, float],
    betas: Mapping[str, float],
    sectors: Mapping[str, str],
) -> dict[str, float]:
    """Take one long and one short per toy sector with equal absolute weights."""

    del betas  # The synthetic example uses identical betas for all four names.
    grouped: dict[str, list[str]] = {}
    for security, sector in sectors.items():
        grouped.setdefault(sector, []).append(security)
    weight = 0.5 / len(grouped)
    result = {security: 0.0 for security in scores}
    for names in grouped.values():
        ordered = sorted(names, key=scores.__getitem__)
        result[ordered[0]] = -weight
        result[ordered[-1]] = weight
    return result


def _synthetic_overlay_policy(market_state: Mapping[str, float]) -> float:
    """Accept a precomputed toy target; the private regime policy is omitted."""

    return market_state["synthetic_target_net_exposure"]


def run_example() -> dict[str, object]:
    information_time = datetime(2026, 1, 5, 21, 0, tzinfo=timezone.utc)
    clock = DecisionClock(
        information_time=information_time,
        execution_time=datetime(2026, 1, 6, 14, 30, tzinfo=timezone.utc),
        pnl_end_time=datetime(2026, 1, 7, 14, 30, tzinfo=timezone.utc),
    )

    testing_start = 100
    training_end = eligible_training_end(
        testing_start=testing_start,
        label_horizon_sessions=5,
        embargo_sessions=2,
    )
    split = WalkForwardSplit(
        training_end=training_end,
        testing_start=testing_start,
        label_horizon_sessions=5,
        embargo_sessions=2,
    )
    split.validate()

    scores = {
        "TECH_LONG": 0.9,
        "TECH_SHORT": -0.7,
        "HEALTH_LONG": 0.6,
        "HEALTH_SHORT": -0.8,
    }
    panel = ResearchPanel.from_rows(
        FeatureRow(name, information_time, {"synthetic_score": score})
        for name, score in scores.items()
    )
    betas = {name: 1.0 for name in scores}
    sectors = {
        "TECH_LONG": "Technology",
        "TECH_SHORT": "Technology",
        "HEALTH_LONG": "Health Care",
        "HEALTH_SHORT": "Health Care",
    }
    pipeline = ReferenceResearchPipeline(
        scorer=_synthetic_scorer,
        alpha_core_builder=_synthetic_neutral_core,
        overlay_policy=_synthetic_overlay_policy,
        expected_features={"synthetic_score"},
    )
    decision = pipeline.decide(
        DecisionInputs(
            clock=clock,
            panel=panel,
            betas=betas,
            sectors=sectors,
            market_state={"synthetic_target_net_exposure": 0.40},
        )
    )

    previous = {name: 0.0 for name in scores}
    synthetic_next_open_returns = {
        "TECH_LONG": 0.012,
        "TECH_SHORT": -0.004,
        "HEALTH_LONG": 0.006,
        "HEALTH_SHORT": 0.002,
    }
    attribution = attribute_one_period(
        layers=decision.layers,
        previous_combined=previous,
        next_open_returns=synthetic_next_open_returns,
        one_way_cost_bps=5.0,
    )
    audit = build_decision_audit(decision, previous, attribution)

    return {
        "clock": {
            "information_time": clock.information_time.isoformat(),
            "execution_time": clock.execution_time.isoformat(),
            "pnl_end_time": clock.pnl_end_time.isoformat(),
        },
        "walk_forward": {
            "training_end": split.training_end,
            "testing_start": split.testing_start,
            "required_purge_sessions": split.required_purge_sessions,
        },
        "scores": dict(decision.scores),
        "layers": {
            "alpha_core": dict(decision.layers.alpha_core),
            "directional_overlay": dict(decision.layers.directional_overlay),
        },
        "one_period_pnl": asdict(attribution),
        "audit": asdict(audit),
    }


def main() -> None:
    print(json.dumps(run_example(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
