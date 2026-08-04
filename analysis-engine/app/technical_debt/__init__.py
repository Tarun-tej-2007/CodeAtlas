"""CodeAtlas Technical Debt domain package."""

from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity
from app.technical_debt.exceptions import TechnicalDebtError, TechnicalDebtRuleError
from app.technical_debt.models import (
    TechnicalDebtItem,
    TechnicalDebtSummary,
    TechnicalDebtReport,
)
from app.technical_debt.analyzer import TechnicalDebtAnalyzer
from app.technical_debt.rule import TechnicalDebtRule
from app.technical_debt.registry import TechnicalDebtRuleRegistry
from app.technical_debt.engine import TechnicalDebtAnalysisEngine
from app.technical_debt.rules.dead_code import DeadCodeRule
from app.technical_debt.rules.deprecated_usage import DeprecatedUsageRule
from app.technical_debt.rules.duplication import DuplicationRule
from app.technical_debt.scoring import TechnicalDebtScorer
from app.technical_debt.context_builder import TechnicalDebtAIContextBuilder

__all__ = [
    "TechnicalDebtCategory",
    "TechnicalDebtSeverity",
    "TechnicalDebtError",
    "TechnicalDebtRuleError",
    "TechnicalDebtItem",
    "TechnicalDebtSummary",
    "TechnicalDebtReport",
    "TechnicalDebtAnalyzer",
    "TechnicalDebtRule",
    "TechnicalDebtRuleRegistry",
    "TechnicalDebtAnalysisEngine",
    "DeadCodeRule",
    "DeprecatedUsageRule",
    "DuplicationRule",
    "TechnicalDebtScorer",
    "TechnicalDebtAIContextBuilder",
]
