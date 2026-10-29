from __future__ import annotations

from proxmox.client import ProxmoxClient
from proxmox.models import GuestKind, PowerAction
from services.guard import (
    ActionGuard,
    AlreadyInStateError,
    InvalidTransitionError,
    ProtectedGuestError,
)
from services.inventory import InventoryService


class PowerService:
    def __init__(
        self,
        client: ProxmoxClient,
        inventory: InventoryService,
        guard: ActionGuard,
    ) -> None:
        self._client = client
        self._inventory = inventory
        self._guard = guard

    async def run_guest_action(
        self,
        kind: GuestKind,
        vmid: int,
        action: PowerAction,
    ) -> str:
        self._guard.assert_not_protected(kind, vmid)
        guest = await self._inventory.get_guest(kind, vmid)
        if guest is None:
            raise GuestNotFoundError(kind, vmid)
        try:
            self._guard.assert_action_allowed(current=guest.status, action=action)
        except AlreadyInStateError:
            return f"Уже в состоянии «{guest.status}»"
        except InvalidTransitionError as exc:
            raise ActionNotAllowedError(exc.action, exc.current) from exc

        await self._client.guest_status_action(kind, vmid, action)
        return "Команда отправлена в Proxmox"

    async def shutdown_host(self) -> str:
        await self._client.shutdown_node()
        return "Команда выключения хоста отправлена"


class GuestNotFoundError(Exception):
    def __init__(self, kind: GuestKind, vmid: int) -> None:
        super().__init__(f"{kind}:{vmid} not found")
        self.kind = kind
        self.vmid = vmid


class ActionNotAllowedError(Exception):
    def __init__(self, action: PowerAction, current: str) -> None:
        super().__init__(f"{action} from {current}")
        self.action = action
        self.current = current
