from __future__ import annotations

import unittest
from datetime import datetime, timezone

from public_reference.accounting import attribute_one_period
from public_reference.contracts import (
    DecisionClock,
    WalkForwardSplit,
    eligible_training_end,
)
from public_reference.portfolio_layers import (
    PortfolioLayers,
    build_directional_overlay,
    validate_alpha_core,
)


class ResearchContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alpha_core = {
            "TECH_LONG": 0.25,
            "TECH_SHORT": -0.25,
            "HEALTH_LONG": 0.25,
            "HEALTH_SHORT": -0.25,
        }
        self.betas = {name: 1.0 for name in self.alpha_core}
        self.sectors = {
            "TECH_LONG": "Technology",
            "TECH_SHORT": "Technology",
            "HEALTH_LONG": "Health Care",
            "HEALTH_SHORT": "Health Care",
        }

    def test_information_precedes_execution_and_pnl(self) -> None:
        clock = DecisionClock(
            datetime(2026, 1, 5, 21, 0, tzinfo=timezone.utc),
            datetime(2026, 1, 6, 14, 30, tzinfo=timezone.utc),
            datetime(2026, 1, 7, 14, 30, tzinfo=timezone.utc),
        )
        clock.validate()
        with self.assertRaises(ValueError):
            DecisionClock(
                clock.execution_time,
                clock.execution_time,
                clock.pnl_end_time,
            ).validate()

    def test_walk_forward_split_rejects_label_overlap(self) -> None:
        testing_start = 100
        valid_training_end = eligible_training_end(testing_start, 5, 2)
        WalkForwardSplit(valid_training_end, testing_start, 5, 2).validate()
        with self.assertRaises(ValueError):
            WalkForwardSplit(95, testing_start, 5, 2).validate()

    def test_alpha_core_and_overlay_have_distinct_jobs(self) -> None:
        validate_alpha_core(self.alpha_core, self.betas, self.sectors)
        overlay = build_directional_overlay(self.alpha_core, 0.40)
        self.assertAlmostEqual(sum(overlay.values()), 0.40)
        self.assertEqual(overlay["TECH_SHORT"], 0.0)
        self.assertEqual(overlay["HEALTH_SHORT"], 0.0)

    def test_sleeves_reconcile_to_total_pnl(self) -> None:
        overlay = build_directional_overlay(self.alpha_core, 0.40)
        layers = PortfolioLayers(self.alpha_core, overlay)
        attribution = attribute_one_period(
            layers=layers,
            previous_combined={name: 0.0 for name in self.alpha_core},
            next_open_returns={
                "TECH_LONG": 0.012,
                "TECH_SHORT": -0.004,
                "HEALTH_LONG": 0.006,
                "HEALTH_SHORT": 0.002,
            },
            one_way_cost_bps=5.0,
        )
        self.assertAlmostEqual(
            attribution.alpha_core_gross
            + attribution.directional_overlay_gross,
            attribution.total_gross,
        )
        self.assertAlmostEqual(
            attribution.total_gross - attribution.transaction_cost,
            attribution.total_net,
        )


if __name__ == "__main__":
    unittest.main()
