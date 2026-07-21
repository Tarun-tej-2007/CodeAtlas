"""Quality rules models module.

Re-exports Diagnostic and Severity models for use within rule implementations.
"""

from app.analyzer.models import Diagnostic, Severity

__all__ = ["Diagnostic", "Severity"]
