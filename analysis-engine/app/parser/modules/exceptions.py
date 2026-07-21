"""Module analysis exceptions module.

Defines the exception hierarchy for import and export analysis operations in CodeAtlas.
"""


class ModuleError(Exception):
    """Base exception class for all module analysis domain errors."""

    pass


class ModuleAnalysisError(ModuleError):
    """Raised when extracting import or export declarations fails."""

    pass
