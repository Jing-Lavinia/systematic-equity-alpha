"""Compact audit record connecting data, timing, exposure, and accounting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from .accounting import PnLAttribution, one_way_turnover
from .portfolio_layers import beta_exposure, sector_exposure
from .research_pipeline import ResearchDecision


@dataclass(frozen=True)
class DecisionAudit:
    information_time: datetime
    execution_time: datetime
    security_count: int
    feature_count: int
    alpha_core_net: float
    alpha_core_beta: float
    maximum_absolute_sector_exposure: float
    directional_overlay_net: float
    combined_gross: float
    one_way_turnover: float
    transaction_cost: float
    gross_reconciliation_gap: float
    net_reconciliation_gap: float

    def validate(self, tolerance: float = 1e-12) -> None:
        if self.information_time >= self.execution_time:
            raise ValueError("audit contains an invalid information clock")
        if self.security_count <= 0 or self.feature_count <= 0:
            raise ValueError("audit contains an empty research cross-section")
        if abs(self.gross_reconciliation_gap) > tolerance:
            raise ValueError("audit found an unreconciled gross P&L gap")
        if abs(self.net_reconciliation_gap) > tolerance:
            raise ValueError("audit found an unreconciled net P&L gap")


def build_decision_audit(
    decision: ResearchDecision,
    previous_combined: Mapping[str, float],
    attribution: PnLAttribution,
) -> DecisionAudit:
    inputs = decision.inputs
    layers = decision.layers
    exposures = layers.diagnostics()
    sectors = sector_exposure(layers.alpha_core, inputs.sectors)
    record = DecisionAudit(
        information_time=inputs.clock.information_time,
        execution_time=inputs.clock.execution_time,
        security_count=len(inputs.panel.securities),
        feature_count=len(inputs.panel.feature_names),
        alpha_core_net=exposures["alpha_core_net"],
        alpha_core_beta=beta_exposure(layers.alpha_core, inputs.betas),
        maximum_absolute_sector_exposure=max(abs(value) for value in sectors.values()),
        directional_overlay_net=exposures["directional_overlay_net"],
        combined_gross=exposures["combined_gross"],
        one_way_turnover=one_way_turnover(previous_combined, layers.combined()),
        transaction_cost=attribution.transaction_cost,
        gross_reconciliation_gap=(
            attribution.alpha_core_gross
            + attribution.directional_overlay_gross
            - attribution.total_gross
        ),
        net_reconciliation_gap=(
            attribution.total_gross
            - attribution.transaction_cost
            - attribution.total_net
        ),
    )
    record.validate()
    return record
