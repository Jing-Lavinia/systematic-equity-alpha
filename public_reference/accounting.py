"""One-period turnover, cost, and sleeve-level P&L reconciliation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .portfolio_layers import PortfolioLayers, Weights, _same_names


def portfolio_pnl(weights: Weights, returns: Mapping[str, float]) -> float:
    names = _same_names(weights, returns)
    return sum(weights[name] * returns[name] for name in names)


def one_way_turnover(previous: Weights, current: Weights) -> float:
    names = _same_names(previous, current)
    return 0.5 * sum(abs(current[name] - previous[name]) for name in names)


@dataclass(frozen=True)
class PnLAttribution:
    alpha_core_gross: float
    directional_overlay_gross: float
    transaction_cost: float
    total_gross: float
    total_net: float

    def validate(self, tolerance: float = 1e-12) -> None:
        sleeve_sum = self.alpha_core_gross + self.directional_overlay_gross
        if abs(sleeve_sum - self.total_gross) > tolerance:
            raise ValueError("sleeve P&L does not reconcile to total gross P&L")
        if abs(self.total_gross - self.transaction_cost - self.total_net) > tolerance:
            raise ValueError("gross P&L minus cost does not reconcile to net P&L")


def attribute_one_period(
    layers: PortfolioLayers,
    previous_combined: Weights,
    next_open_returns: Mapping[str, float],
    one_way_cost_bps: float,
) -> PnLAttribution:
    """Attribute one next-open return interval and charge turnover once."""

    combined = layers.combined()
    alpha_core_gross = portfolio_pnl(layers.alpha_core, next_open_returns)
    directional_overlay_gross = portfolio_pnl(
        layers.directional_overlay,
        next_open_returns,
    )
    total_gross = portfolio_pnl(combined, next_open_returns)
    transaction_cost = (
        one_way_turnover(previous_combined, combined)
        * one_way_cost_bps
        / 10_000.0
    )
    result = PnLAttribution(
        alpha_core_gross=alpha_core_gross,
        directional_overlay_gross=directional_overlay_gross,
        transaction_cost=transaction_cost,
        total_gross=total_gross,
        total_net=total_gross - transaction_cost,
    )
    result.validate()
    return result
