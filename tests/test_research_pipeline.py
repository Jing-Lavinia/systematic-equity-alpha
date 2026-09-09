from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from typing import Mapping

from public_reference.contracts import DecisionClock
from public_reference.data_contracts import FeatureRow, ResearchPanel
from public_reference.research_pipeline import (
    DecisionInputs,
    ReferenceResearchPipeline,
)
from public_reference.walkthrough import run_example


def score_panel(panel: ResearchPanel) -> dict[str, float]:
    return {
        security: values["score"]
        for security, values in panel.as_feature_matrix().items()
    }


def build_neutral_core(
    scores: Mapping[str, float],
    betas: Mapping[str, float],
    sectors: Mapping[str, str],
) -> dict[str, float]:
    del scores, betas, sectors
    return {"A": 0.25, "B": -0.25, "C": 0.25, "D": -0.25}


def overlay_policy(market_state: Mapping[str, float]) -> float:
    return market_state["target"]


class ResearchPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        information_time = datetime(2026, 1, 5, 21, 0, tzinfo=timezone.utc)
        self.panel = ResearchPanel.from_rows(
            FeatureRow(name, information_time, {"score": score})
            for name, score in {"A": 0.9, "B": -0.7, "C": 0.6, "D": -0.8}.items()
        )
        self.inputs = DecisionInputs(
            clock=DecisionClock(
                information_time,
                information_time + timedelta(hours=17, minutes=30),
                information_time + timedelta(days=1, hours=17, minutes=30),
            ),
            panel=self.panel,
            betas={name: 1.0 for name in "ABCD"},
            sectors={"A": "X", "B": "X", "C": "Y", "D": "Y"},
            market_state={"target": 0.4},
        )
        self.pipeline = ReferenceResearchPipeline(
            scorer=score_panel,
            alpha_core_builder=build_neutral_core,
            overlay_policy=overlay_policy,
            expected_features={"score"},
        )

    def test_pipeline_connects_scores_core_and_overlay(self) -> None:
        decision = self.pipeline.decide(self.inputs)
        self.assertEqual(set(decision.scores), set("ABCD"))
        self.assertAlmostEqual(sum(decision.layers.alpha_core.values()), 0.0)
        self.assertAlmostEqual(sum(decision.layers.directional_overlay.values()), 0.4)

    def test_future_panel_is_rejected(self) -> None:
        late_panel = ResearchPanel.from_rows(
            FeatureRow(
                row.security,
                self.inputs.clock.execution_time,
                row.values,
            )
            for row in self.panel.rows
        )
        with self.assertRaises(ValueError):
            self.pipeline.decide(
                DecisionInputs(
                    clock=self.inputs.clock,
                    panel=late_panel,
                    betas=self.inputs.betas,
                    sectors=self.inputs.sectors,
                    market_state=self.inputs.market_state,
                )
            )

    def test_incomplete_scores_are_rejected(self) -> None:
        incomplete_pipeline = ReferenceResearchPipeline(
            scorer=lambda panel: {"A": 1.0},
            alpha_core_builder=build_neutral_core,
            overlay_policy=overlay_policy,
            expected_features={"score"},
        )
        with self.assertRaises(ValueError):
            incomplete_pipeline.decide(self.inputs)

    def test_non_neutral_core_is_rejected(self) -> None:
        non_neutral_pipeline = ReferenceResearchPipeline(
            scorer=score_panel,
            alpha_core_builder=lambda scores, betas, sectors: {
                name: 0.25 for name in scores
            },
            overlay_policy=overlay_policy,
            expected_features={"score"},
        )
        with self.assertRaises(ValueError):
            non_neutral_pipeline.decide(self.inputs)

    def test_walkthrough_produces_a_reconciled_audit(self) -> None:
        result = run_example()
        audit = result["audit"]
        self.assertEqual(audit["security_count"], 4)
        self.assertAlmostEqual(audit["alpha_core_net"], 0.0)
        self.assertAlmostEqual(audit["gross_reconciliation_gap"], 0.0)
        self.assertAlmostEqual(audit["net_reconciliation_gap"], 0.0)


if __name__ == "__main__":
    unittest.main()
