"""Executable public reference for the Systematic Equity Alpha architecture."""

from .accounting import PnLAttribution, attribute_one_period
from .audit import DecisionAudit, build_decision_audit
from .contracts import DecisionClock, WalkForwardSplit
from .data_contracts import FeatureRow, ResearchPanel
from .portfolio_layers import PortfolioLayers
from .research_pipeline import (
    DecisionInputs,
    ReferenceResearchPipeline,
    ResearchDecision,
)

__all__ = [
    "DecisionClock",
    "DecisionAudit",
    "DecisionInputs",
    "FeatureRow",
    "PnLAttribution",
    "PortfolioLayers",
    "ReferenceResearchPipeline",
    "ResearchDecision",
    "ResearchPanel",
    "WalkForwardSplit",
    "attribute_one_period",
    "build_decision_audit",
]
