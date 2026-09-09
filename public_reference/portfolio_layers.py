"""Transparent portfolio-layer composition and exposure diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


Weights = Mapping[str, float]


def _same_names(*vectors: Mapping[str, object]) -> set[str]:
    names = set(vectors[0])
    if any(set(vector) != names for vector in vectors[1:]):
        raise ValueError("all inputs must contain the same security names")
    return names


def net_exposure(weights: Weights) -> float:
    return sum(weights.values())


def gross_exposure(weights: Weights) -> float:
    return sum(abs(weight) for weight in weights.values())


def beta_exposure(weights: Weights, betas: Mapping[str, float]) -> float:
    names = _same_names(weights, betas)
    return sum(weights[name] * betas[name] for name in names)


def sector_exposure(
    weights: Weights,
    sectors: Mapping[str, str],
) -> dict[str, float]:
    _same_names(weights, sectors)
    result: dict[str, float] = {}
    for name, weight in weights.items():
        sector = sectors[name]
        result[sector] = result.get(sector, 0.0) + weight
    return result


def validate_alpha_core(
    weights: Weights,
    betas: Mapping[str, float],
    sectors: Mapping[str, str],
    tolerance: float = 1e-8,
) -> None:
    """Check the public invariants for a market-neutral stock-selection sleeve."""

    if abs(net_exposure(weights)) > tolerance:
        raise ValueError("Alpha Core is not dollar neutral")
    if abs(beta_exposure(weights, betas)) > tolerance:
        raise ValueError("Alpha Core is not beta neutral")
    if any(abs(value) > tolerance for value in sector_exposure(weights, sectors).values()):
        raise ValueError("Alpha Core is not sector neutral")


def build_directional_overlay(
    alpha_core: Weights,
    target_net_exposure: float,
) -> dict[str, float]:
    """Spread directional exposure across names in the Alpha Core long book."""

    if target_net_exposure < 0:
        raise ValueError("this public example supports long overlays only")
    long_names = [name for name, weight in alpha_core.items() if weight > 0]
    if target_net_exposure and not long_names:
        raise ValueError("a long overlay requires Alpha Core long names")
    allocation = target_net_exposure / len(long_names) if long_names else 0.0
    return {
        name: allocation if name in long_names else 0.0
        for name in alpha_core
    }


@dataclass(frozen=True)
class PortfolioLayers:
    """Two separately governed sleeves that combine into executable weights."""

    alpha_core: Weights
    directional_overlay: Weights

    def combined(self) -> dict[str, float]:
        names = _same_names(self.alpha_core, self.directional_overlay)
        return {
            name: self.alpha_core[name] + self.directional_overlay[name]
            for name in names
        }

    def diagnostics(self) -> dict[str, float]:
        combined = self.combined()
        return {
            "alpha_core_net": net_exposure(self.alpha_core),
            "directional_overlay_net": net_exposure(self.directional_overlay),
            "combined_net": net_exposure(combined),
            "combined_gross": gross_exposure(combined),
        }
