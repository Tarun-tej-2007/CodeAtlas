"""Scanner configuration module.

Defines the ScannerConfig model for controlling scanner policies such as
symlink traversal, hidden file inclusion, default filters, and statistics collection.
"""

from pydantic import BaseModel, ConfigDict, Field


class ScannerConfig(BaseModel):
    """Configuration options for repository scanning behavior."""

    follow_symlinks: bool = Field(
        default=False,
        description="Whether to traverse directory symlinks and include file symlinks.",
    )
    include_hidden: bool = Field(
        default=False,
        description="Whether to process hidden dot-prefixed directories and files.",
    )
    respect_default_filters: bool = Field(
        default=True,
        description="Whether to apply built-in ignored directory and file filter sets.",
    )
    collect_statistics: bool = Field(
        default=True,
        description="Whether to aggregate scan performance metrics and counters.",
    )

    model_config = ConfigDict(frozen=True)
