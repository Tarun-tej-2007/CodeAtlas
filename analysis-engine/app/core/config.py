"""Configuration settings for the CodeAtlas Analysis Engine."""

import os
from pathlib import Path


class Settings:
    """Settings class loading configuration variables from the environment."""

    # Workspace settings
    WORKSPACE_ROOT: Path = Path(os.getenv("WORKSPACE_ROOT", "/tmp/codeatlas"))
    KEEP_WORKSPACE: bool = os.getenv("KEEP_WORKSPACE", "false").lower() == "true"


# Global configuration instance
settings = Settings()
