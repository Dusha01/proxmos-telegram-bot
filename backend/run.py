from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("APP_ENV", "dev") == "dev" and os.getenv("API_RELOAD", "0") == "1"
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )


if __name__ == "__main__":
    main()
