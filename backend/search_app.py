from __future__ import annotations

from pathlib import Path
from typing import Any

from .app import create_app
from .intent import mount_search

app = create_app()


def _house_visible(record: dict[str, Any]) -> bool:
    return str(record.get("visibility", "PRIVATE")).upper() in {"HOUSE", "PUBLIC"}


mount_search(app, Path(app.state.repo_root), app.state.store, _house_visible)
