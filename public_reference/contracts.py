"""Information-clock and walk-forward contracts.

The objects in this module make timing assumptions explicit. They contain no
strategy features, fitted models, or private research parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DecisionClock:
    """Describe one decision without allowing a return to precede execution."""

    information_time: datetime
    execution_time: datetime
    pnl_end_time: datetime

    def validate(self) -> None:
        if self.information_time >= self.execution_time:
            raise ValueError("information must be available before execution")
        if self.execution_time >= self.pnl_end_time:
            raise ValueError("P&L must be measured after execution")


@dataclass(frozen=True)
class WalkForwardSplit:
    """A training/test split with label resolution and embargo separation."""

    training_end: int
    testing_start: int
    label_horizon_sessions: int
    embargo_sessions: int = 0

    @property
    def required_purge_sessions(self) -> int:
        return max(self.label_horizon_sessions + 1, self.embargo_sessions)

    def validate(self) -> None:
        if self.label_horizon_sessions < 0 or self.embargo_sessions < 0:
            raise ValueError("purge inputs must be non-negative")
        if self.training_end + self.required_purge_sessions >= self.testing_start:
            raise ValueError("training labels overlap the evaluation boundary")


def eligible_training_end(
    testing_start: int,
    label_horizon_sessions: int,
    embargo_sessions: int = 0,
) -> int:
    """Return the latest training index that satisfies the split contract."""

    purge = max(label_horizon_sessions + 1, embargo_sessions)
    return testing_start - purge - 1
