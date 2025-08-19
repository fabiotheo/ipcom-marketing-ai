"""Version management for OSP Marketing Tools."""

import sys
from pathlib import Path
from typing import Any, Dict

# Handle Python 3.10 compatibility (tomllib available from 3.11+)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        # This should not happen in normal circumstances due to pyproject.toml dependency
        raise ImportError("tomli package required for Python < 3.11")


def get_version() -> str:
    """Get the current version from pyproject.toml."""
    try:
        # Find pyproject.toml by traversing up from this file
        current_path = Path(__file__).parent
        while current_path != current_path.parent:
            pyproject_path = current_path / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data: Dict[str, Any] = tomllib.load(f)
                    return str(data["project"]["version"])
            current_path = current_path.parent

        # Fallback: try from project root
        root_path = Path(__file__).parent.parent.parent
        pyproject_path = root_path / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                project_data: Dict[str, Any] = tomllib.load(f)
                return str(project_data["project"]["version"])

        # Last fallback
        return "0.4.0"
    except Exception:
        # Fallback version if file reading fails
        return "0.4.0"


# Cache the version to avoid repeated file reads
__version__ = get_version()
