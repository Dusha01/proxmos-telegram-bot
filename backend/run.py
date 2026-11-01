from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

_BACKEND_ROOT = Path(__file__).resolve().parent
_BACKEND_SRC = _BACKEND_ROOT / "src"


def _bootstrap() -> None:
    src = str(_BACKEND_SRC)
    if src not in sys.path:
        sys.path.insert(0, src)
    current = os.environ.get("PYTHONPATH", "")
    if src not in current.split(os.pathsep):
        os.environ["PYTHONPATH"] = src if not current else f"{src}{os.pathsep}{current}"


def main() -> None:
    _bootstrap()
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("APP_ENV", "dev") == "dev" and os.getenv("API_RELOAD", "0") == "1"
    if reload:
        uvicorn.run(
            "api.app:app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=[str(_BACKEND_SRC)],
            factory=False,
        )
        return
    from api.app import app

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
