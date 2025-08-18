"""Version management for OSP Marketing Tools."""

import tomllib  # type: ignore
from pathlib import Path


def get_version() -> str:
    """Get the current version from pyproject.toml."""
    try:
        # Find pyproject.toml by traversing up from this file
        current_path = Path(__file__).parent
        while current_path != current_path.parent:
            pyproject_path = current_path / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return str(data["project"]["version"])
            current_path = current_path.parent

        # Fallback: try from project root
        root_path = Path(__file__).parent.parent.parent
        pyproject_path = root_path / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return str(data["project"]["version"])

        # Last fallback
        return "0.3.0"
    except Exception:
        # Fallback version if file reading fails
        return "0.3.0"


# Cache the version to avoid repeated file reads
__version__ = get_version()
