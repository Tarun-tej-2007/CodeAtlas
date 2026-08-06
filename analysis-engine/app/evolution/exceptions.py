"""Domain-specific exception definitions for Architecture Evolution."""


class EvolutionError(Exception):
    """Base domain exception class for all architecture evolution failures."""

    pass


class EvolutionValidationError(EvolutionError):
    """Raised when request payload or model properties fail validation rules."""

    pass
