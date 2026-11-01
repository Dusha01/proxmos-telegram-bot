from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_BOT_ROOT = Path(__file__).resolve().parent


def _bootstrap() -> None:
    root = str(_BOT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    current = os.environ.get("PYTHONPATH", "")
    if root not in current.split(os.pathsep):
        os.environ["PYTHONPATH"] = root if not current else f"{root}{os.pathsep}{current}"


def main() -> None:
    _bootstrap()
    from core.main import main as run_bot

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
