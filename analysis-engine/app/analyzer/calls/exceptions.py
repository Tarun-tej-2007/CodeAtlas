"""Call analysis exceptions module.

Defines the exception hierarchy for intra-file call analysis in CodeAtlas.
"""


class CallError(Exception):
    """Base exception class for all call analysis domain errors."""

    pass


class CallAnalysisError(CallError):
    """Raised when call detection or analysis fails."""

    pass
