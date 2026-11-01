from __future__ import annotations

import os
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


def resolve_env_file() -> str | None:
    override = os.getenv("ENV_FILE")
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            path = (_BACKEND_ROOT / path).resolve()
        if path.is_file():
            return str(path)
        return None
    for name in (".env.dev", ".env.prod"):
        candidate = _BACKEND_ROOT / name
        if candidate.is_file():
            return str(candidate)
    return None
