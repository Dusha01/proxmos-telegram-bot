from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

_MOCK_ROOT = Path(__file__).resolve().parent


def _bootstrap() -> None:
    root = str(_MOCK_ROOT)
    os.chdir(root)
    if root not in sys.path:
        sys.path.insert(0, root)
    current = os.environ.get("PYTHONPATH", "")
    if root not in current.split(os.pathsep):
        os.environ["PYTHONPATH"] = root if not current else f"{root}{os.pathsep}{current}"


def main() -> None:
    _bootstrap()
    host = os.getenv("MOCK_HOST", "0.0.0.0")
    port = int(os.getenv("MOCK_PORT", "8006"))
    from app import app

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
