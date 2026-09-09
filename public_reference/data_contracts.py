"""Synthetic cross-sectional data contracts used by the public pipeline.

The private project has source-specific loaders and a larger validation layer.
This module keeps only the checks needed to show how a research decision is
anchored to one observable information set.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from numbers import Real
from typing import Iterable, Mapping


@dataclass(frozen=True)
class FeatureRow:
    security: str
    information_time: datetime
    values: Mapping[str, float]

    def validate(self) -> None:
        if not self.security:
            raise ValueError("security identifier cannot be empty")
        if not self.values:
            raise ValueError("a feature row cannot be empty")
        for feature, value in self.values.items():
            if not feature:
                raise ValueError("feature name cannot be empty")
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"feature {feature!r} must be numeric")
            if not isfinite(float(value)):
                raise ValueError(f"feature {feature!r} must be finite")


@dataclass(frozen=True)
class ResearchPanel:
    """One cross-section whose rows share an information timestamp and schema."""

    rows: tuple[FeatureRow, ...]

    @classmethod
    def from_rows(cls, rows: Iterable[FeatureRow]) -> "ResearchPanel":
        return cls(tuple(rows))

    @property
    def securities(self) -> set[str]:
        return {row.security for row in self.rows}

    @property
    def information_time(self) -> datetime:
        if not self.rows:
            raise ValueError("research panel cannot be empty")
        return self.rows[0].information_time

    @property
    def feature_names(self) -> set[str]:
        if not self.rows:
            return set()
        return set(self.rows[0].values)

    def validate(self, expected_features: set[str] | None = None) -> None:
        if not self.rows:
            raise ValueError("research panel cannot be empty")
        for row in self.rows:
            row.validate()
        if len(self.securities) != len(self.rows):
            raise ValueError("research panel contains duplicate securities")
        if len({row.information_time for row in self.rows}) != 1:
            raise ValueError("all rows must share one information timestamp")
        if any(set(row.values) != self.feature_names for row in self.rows):
            raise ValueError("all rows must share one feature schema")
        if expected_features is not None and self.feature_names != expected_features:
            raise ValueError("research panel does not match the expected feature schema")

    def as_feature_matrix(self) -> dict[str, dict[str, float]]:
        return {row.security: dict(row.values) for row in self.rows}
