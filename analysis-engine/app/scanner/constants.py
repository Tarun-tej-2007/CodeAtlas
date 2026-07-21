"""Scanner domain constants module.

Defines default extension filters, ignored directories, and ignored files
used during codebase scanning operations.
"""

from typing import Final

SUPPORTED_EXTENSIONS: Final[set[str]] = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}

EXTENSION_LANGUAGE_MAP: Final[dict[str, str]] = {
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}

IGNORED_DIRECTORIES: Final[set[str]] = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".idea",
    ".vscode",
    "__pycache__",
}

IGNORED_FILES: Final[set[str]] = {
    ".DS_Store",
}
