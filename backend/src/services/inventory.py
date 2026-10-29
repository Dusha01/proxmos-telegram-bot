from __future__ import annotations

from proxmox.client import ProxmoxClient
from proxmox.models import Guest, GuestKind, GuestListResponse, NodeStatus, SummaryResponse
from services.guard import guest_from_raw, node_from_raw


class InventoryService:
    def __init__(self, client: ProxmoxClient) -> None:
        self._client = client

    async def get_node(self) -> NodeStatus:
        raw = await self._client.get_node_status()
        return node_from_raw(raw)

    async def list_guests(self, kind: GuestKind) -> GuestListResponse:
        if kind == "qemu":
            raw_list = await self._client.list_qemu()
        else:
            raw_list = await self._client.list_lxc()
        items = [guest_from_raw(item, kind) for item in raw_list]
        items.sort(key=lambda g: g.vmid)
        return GuestListResponse(items=items, total=len(items))

    async def get_guest(self, kind: GuestKind, vmid: int) -> Guest | None:
        response = await self.list_guests(kind)
        for guest in response.items:
            if guest.vmid == vmid:
                return guest
        return None

    async def get_summary(self) -> SummaryResponse:
        node = await self.get_node()
        qemu = await self.list_guests("qemu")
        lxc = await self.list_guests("lxc")
        return SummaryResponse(
            node=node,
            qemu_total=qemu.total,
            qemu_running=sum(1 for g in qemu.items if g.status == "running"),
            lxc_total=lxc.total,
            lxc_running=sum(1 for g in lxc.items if g.status == "running"),
        )
