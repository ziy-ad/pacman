import sys
from pathlib import Path


def resource_path(rel: str) -> Path:
    """Bundled read-only files: images, fonts."""
    base = Path(
        getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
        )
    return base / rel


def user_path(rel: str) -> Path:
    """Files next to the executable: config.json, score files."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent
    return base / rel
