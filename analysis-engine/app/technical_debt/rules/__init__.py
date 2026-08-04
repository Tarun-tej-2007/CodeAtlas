"""Technical Debt Concrete Rules package."""

from app.technical_debt.rules.dead_code import DeadCodeRule
from app.technical_debt.rules.deprecated_usage import DeprecatedUsageRule
from app.technical_debt.rules.duplication import DuplicationRule

__all__ = [
    "DeadCodeRule",
    "DeprecatedUsageRule",
    "DuplicationRule",
]
