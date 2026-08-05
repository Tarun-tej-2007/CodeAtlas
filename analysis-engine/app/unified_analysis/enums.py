"""Unified Analysis Enums Module."""

from enum import Enum


class AnalysisStatus(str, Enum):
    """Represents the execution status of the Unified Analysis run."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
