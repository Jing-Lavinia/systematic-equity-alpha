"""End-to-end orchestration with explicit private-component boundaries.

The public pipeline owns validation and sequencing. Feature transformations,
fitted estimators, the production optimizer, and the real overlay policy are
injected interfaces and are not represented as public strategy code.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable, Mapping

from .contracts import DecisionClock
from .data_contracts import ResearchPanel
from .portfolio_layers import (
    PortfolioLayers,
    Weights,
    build_directional_overlay,
    validate_alpha_core,
)


CrossSectionalScorer = Callable[[ResearchPanel], Mapping[str, float]]
AlphaCoreBuilder = Callable[
    [Mapping[str, float], Mapping[str, float], Mapping[str, str]],
    Weights,
]
OverlayPolicy = Callable[[Mapping[str, float]], float]


def _validate_named_numbers(
    values: Mapping[str, float],
    expected_names: set[str],
    label: str,
) -> None:
    if set(values) != expected_names:
        raise ValueError(f"{label} must cover the full decision cross-section")
    if any(not isfinite(float(value)) for value in values.values()):
        raise ValueError(f"{label} must contain only finite values")


@dataclass(frozen=True)
class DecisionInputs:
    clock: DecisionClock
    panel: ResearchPanel
    betas: Mapping[str, float]
    sectors: Mapping[str, str]
    market_state: Mapping[str, float]


@dataclass(frozen=True)
class ResearchDecision:
    """Reviewable output from one cross-sectional portfolio decision."""

    inputs: DecisionInputs
    scores: Mapping[str, float]
    layers: PortfolioLayers


@dataclass(frozen=True)
class ReferenceResearchPipeline:
    """Sequence the public contracts around three protected research choices."""

    scorer: CrossSectionalScorer
    alpha_core_builder: AlphaCoreBuilder
    overlay_policy: OverlayPolicy
    expected_features: set[str] | None = None

    def decide(self, inputs: DecisionInputs) -> ResearchDecision:
        inputs.clock.validate()
        inputs.panel.validate(self.expected_features)
        if inputs.panel.information_time > inputs.clock.information_time:
            raise ValueError("panel contains information unavailable at decision time")

        names = inputs.panel.securities
        _validate_named_numbers(inputs.betas, names, "betas")
        if set(inputs.sectors) != names:
            raise ValueError("sectors must cover the full decision cross-section")

        scores = dict(self.scorer(inputs.panel))
        _validate_named_numbers(scores, names, "scores")

        alpha_core = dict(
            self.alpha_core_builder(scores, inputs.betas, inputs.sectors)
        )
        _validate_named_numbers(alpha_core, names, "Alpha Core weights")
        validate_alpha_core(alpha_core, inputs.betas, inputs.sectors)

        overlay_target = float(self.overlay_policy(inputs.market_state))
        if not isfinite(overlay_target):
            raise ValueError("overlay target must be finite")
        directional_overlay = build_directional_overlay(
            alpha_core,
            target_net_exposure=overlay_target,
        )
        return ResearchDecision(
            inputs=inputs,
            scores=scores,
            layers=PortfolioLayers(alpha_core, directional_overlay),
        )
