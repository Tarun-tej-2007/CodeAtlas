"""Configuration settings for the CodeAtlas Analysis Engine."""

import os
from pathlib import Path


class Settings:
    """Settings class loading configuration variables from the environment."""

    # Workspace settings
    WORKSPACE_ROOT: Path = Path(os.getenv("WORKSPACE_ROOT", "/tmp/codeatlas"))
    KEEP_WORKSPACE: bool = os.getenv("KEEP_WORKSPACE", "false").lower() == "true"

    # AI Service Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_ENDPOINT: str = os.getenv("OPENAI_API_ENDPOINT", "")
    OPENAI_TIMEOUT_SECONDS: int = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))
    OPENAI_MAX_RETRIES: int = int(os.getenv("OPENAI_MAX_RETRIES", "0"))


# Global configuration instance
settings = Settings()
