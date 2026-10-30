from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorClient

from core.settings import Settings, get_settings
from db.models.dto import AdminOut
from db.repositories.repo import AdminRepository, create_motor_client
from proxmox.client import ProxmoxClient, ProxmoxError
from proxmox.models import Guest, GuestKind, GuestListResponse, NodeStatus, PowerAction, SummaryResponse
from services.guard import ActionGuard, ProtectedGuestError
from services.inventory import InventoryService
from services.power import ActionNotAllowedError, GuestNotFoundError, PowerService

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    settings: Settings
    mongo_client: AsyncIOMotorClient
    admins: AdminRepository
    proxmox: ProxmoxClient
    inventory: InventoryService
    power: PowerService


def _configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _configure_logging(settings)
    mongo_client = create_motor_client(settings.mongo_url)
    admins = AdminRepository(mongo_client[settings.mongo_db])
    await admins.ensure_indexes()
    await admins.ensure_from_env(
        settings.admin_user_id,
        settings.admin_chat_id,
        settings.admin_name or None,
    )
    proxmox = ProxmoxClient(
        host=settings.proxmox_host,
        token_id=settings.proxmox_token_id,
        token_secret=settings.proxmox_token_secret,
        node=settings.proxmox_node,
        verify_ssl=settings.proxmox_verify_ssl,
    )
    guard = ActionGuard(settings.protected_guest_keys())
    inventory = InventoryService(proxmox)
    power = PowerService(proxmox, inventory, guard)
    app.state.container = AppState(
        settings=settings,
        mongo_client=mongo_client,
        admins=admins,
        proxmox=proxmox,
        inventory=inventory,
        power=power,
    )
    logger.info("API started (env=%s)", settings.app_env)
    yield
    mongo_client.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Proxmox Bot API", lifespan=lifespan)

    def get_container() -> AppState:
        return app.state.container

    def verify_bot_token(
        x_bot_token: Annotated[str | None, Header()] = None,
        container: AppState = Depends(get_container),
    ) -> None:
        if not x_bot_token or x_bot_token != container.settings.bot_api_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    async def require_admin(
        x_telegram_user_id: Annotated[int | None, Header()] = None,
        x_telegram_chat_id: Annotated[int | None, Header()] = None,
        container: AppState = Depends(get_container),
    ) -> AdminOut:
        if x_telegram_user_id is None or x_telegram_chat_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        admin = await container.admins.find_active(x_telegram_user_id, x_telegram_chat_id)
        if admin is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return admin

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/access", status_code=status.HTTP_204_NO_CONTENT)
    async def check_access(
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
    ) -> None:
        return None

    @app.get("/node", response_model=NodeStatus)
    async def get_node(
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
        container: AppState = Depends(get_container),
    ) -> NodeStatus:
        try:
            return await container.inventory.get_node()
        except ProxmoxError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get("/summary", response_model=SummaryResponse)
    async def get_summary(
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
        container: AppState = Depends(get_container),
    ) -> SummaryResponse:
        try:
            return await container.inventory.get_summary()
        except ProxmoxError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get("/guests", response_model=GuestListResponse)
    async def list_guests(
        kind: Annotated[GuestKind, Query()],
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
        container: AppState = Depends(get_container),
    ) -> GuestListResponse:
        try:
            return await container.inventory.list_guests(kind)
        except ProxmoxError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get("/guests/{kind}/{vmid}", response_model=Guest)
    async def get_guest(
        kind: GuestKind,
        vmid: int,
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
        container: AppState = Depends(get_container),
    ) -> Guest:
        try:
            guest = await container.inventory.get_guest(kind, vmid)
        except ProxmoxError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        if guest is None:
            raise HTTPException(status_code=404, detail="Guest not found")
        return guest

    @app.post("/guests/{kind}/{vmid}/{action}")
    async def guest_action(
        kind: GuestKind,
        vmid: int,
        action: PowerAction,
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
        container: AppState = Depends(get_container),
    ) -> dict[str, str]:
        try:
            message = await container.power.run_guest_action(kind, vmid, action)
        except ProtectedGuestError:
            raise HTTPException(status_code=403, detail="Guest is protected") from None
        except GuestNotFoundError:
            raise HTTPException(status_code=404, detail="Guest not found") from None
        except ActionNotAllowedError as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Action {exc.action} not allowed from {exc.current}",
            ) from exc
        except ProxmoxError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"message": message}

    @app.post("/node/shutdown")
    async def node_shutdown(
        _: None = Depends(verify_bot_token),
        __: AdminOut = Depends(require_admin),
        container: AppState = Depends(get_container),
    ) -> dict[str, str]:
        try:
            message = await container.power.shutdown_host()
        except ProxmoxError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"message": message}

    return app


app = create_app()
