from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from state import ClusterState, MockStateError, PowerAction

logger = logging.getLogger(__name__)

NODE = "pve"
state = ClusterState.from_fixture()


def create_app() -> FastAPI:
    app = FastAPI(title="Proxmox API Mock", docs_url=None, redoc_url=None)

    def proxmox_data(data: Any) -> JSONResponse:
        return JSONResponse({"data": data})

    @app.get("/api2/json/nodes")
    async def get_nodes() -> JSONResponse:
        return proxmox_data(state.list_nodes())

    @app.get(f"/api2/json/nodes/{NODE}/status")
    async def get_node_status() -> JSONResponse:
        return proxmox_data(state.node_status())

    @app.get(f"/api2/json/nodes/{NODE}/qemu")
    async def list_qemu() -> JSONResponse:
        return proxmox_data(state.list_guests("qemu"))

    @app.get(f"/api2/json/nodes/{NODE}/lxc")
    async def list_lxc() -> JSONResponse:
        return proxmox_data(state.list_guests("lxc"))

    @app.post(f"/api2/json/nodes/{NODE}/{{kind}}/{{vmid}}/status/{{action}}")
    async def guest_action(kind: str, vmid: int, action: str) -> JSONResponse:
        if kind not in ("qemu", "lxc"):
            raise HTTPException(status_code=404, detail="unknown guest kind")
        if action not in ("start", "stop", "shutdown", "suspend", "resume"):
            raise HTTPException(status_code=400, detail="unknown action")
        try:
            state.apply_guest_action(kind, vmid, action)  # type: ignore[arg-type]
        except MockStateError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        logger.info("guest action %s %s:%s -> ok", action, kind, vmid)
        return proxmox_data(None)

    @app.post(f"/api2/json/nodes/{NODE}/status")
    async def node_status_command(request: Request) -> JSONResponse:
        body: dict[str, Any] = {}
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.json()
        else:
            form = await request.form()
            body = dict(form)
        command = body.get("command")
        if command != "shutdown":
            raise HTTPException(status_code=400, detail="unsupported command")
        state.record_node_shutdown()
        logger.warning("mock: node shutdown command received (demo stack keeps running)")
        return proxmox_data(None)

    @app.post("/mock/reset")
    async def reset_state() -> dict[str, str]:
        if os.getenv("MOCK_ALLOW_RESET", "1") != "1":
            raise HTTPException(status_code=403, detail="reset disabled")
        state.reset()
        return {"status": "reset"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
