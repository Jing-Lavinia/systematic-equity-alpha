from __future__ import annotations

import unittest
from datetime import datetime, timezone

from public_reference.data_contracts import FeatureRow, ResearchPanel


class DataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.information_time = datetime(2026, 1, 5, 21, 0, tzinfo=timezone.utc)

    def row(self, security: str, **values: float) -> FeatureRow:
        return FeatureRow(security, self.information_time, values)

    def test_valid_panel_has_one_cross_sectional_schema(self) -> None:
        panel = ResearchPanel.from_rows(
            [
                self.row("AAA", value=0.5, volatility=0.2),
                self.row("BBB", value=-0.4, volatility=0.3),
            ]
        )
        panel.validate({"value", "volatility"})
        self.assertEqual(panel.securities, {"AAA", "BBB"})

    def test_duplicate_security_is_rejected(self) -> None:
        panel = ResearchPanel.from_rows(
            [self.row("AAA", value=0.5), self.row("AAA", value=-0.4)]
        )
        with self.assertRaises(ValueError):
            panel.validate()

    def test_mixed_feature_schema_is_rejected(self) -> None:
        panel = ResearchPanel.from_rows(
            [self.row("AAA", value=0.5), self.row("BBB", other=-0.4)]
        )
        with self.assertRaises(ValueError):
            panel.validate()

    def test_non_finite_feature_is_rejected(self) -> None:
        panel = ResearchPanel.from_rows([self.row("AAA", value=float("nan"))])
        with self.assertRaises(ValueError):
            panel.validate()


if __name__ == "__main__":
    unittest.main()
