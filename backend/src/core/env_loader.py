from __future__ import annotations

import os
from pathlib import Path


def resolve_env_file() -> str | None:
    env_file = os.getenv("ENV_FILE", ".env.dev")
    path = Path(env_file)
    if path.is_file():
        return str(path.resolve())
    return None
