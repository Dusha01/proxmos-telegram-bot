from __future__ import annotations

from proxmox.models import Guest, GuestKind, GuestStatus, NodeStatus, PowerAction


def _map_status(raw: str | None) -> GuestStatus:
    if raw == "running":
        return "running"
    if raw == "stopped":
        return "stopped"
    if raw == "paused":
        return "paused"
    return "unknown"


def guest_from_raw(raw: dict, kind: GuestKind) -> Guest:
    vmid = int(raw.get("vmid", 0))
    name = str(raw.get("name") or f"{kind}-{vmid}")
    status = _map_status(raw.get("status"))
    return Guest(vmid=vmid, name=name, kind=kind, status=status)


def _as_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_node_status_raw(raw: dict) -> dict:
    """Map Proxmox VE 9+ nested status fields to legacy flat keys used by the bot."""
    normalized = dict(raw)
    memory = raw.get("memory")
    if isinstance(memory, dict):
        if normalized.get("mem") is None:
            normalized["mem"] = _as_int(memory.get("used"))
        if normalized.get("maxmem") is None:
            normalized["maxmem"] = _as_int(memory.get("total"))
    rootfs = raw.get("rootfs")
    if isinstance(rootfs, dict):
        if normalized.get("disk") is None:
            normalized["disk"] = _as_int(rootfs.get("used"))
        if normalized.get("maxdisk") is None:
            normalized["maxdisk"] = _as_int(rootfs.get("total"))
    cpuinfo = raw.get("cpuinfo")
    if isinstance(cpuinfo, dict) and normalized.get("maxcpu") is None:
        normalized["maxcpu"] = _as_int(cpuinfo.get("cpus"))
    return normalized


def node_from_raw(raw: dict) -> NodeStatus:
    raw = normalize_node_status_raw(raw)
    loadavg = raw.get("loadavg") or []
    if isinstance(loadavg, str):
        loadavg = [float(x) for x in loadavg.split() if x]
    elif isinstance(loadavg, list):
        loadavg = [float(x) for x in loadavg]
    else:
        loadavg = []
    return NodeStatus(
        node=str(raw.get("node", "")),
        uptime=raw.get("uptime"),
        cpu=raw.get("cpu"),
        maxcpu=raw.get("maxcpu"),
        mem=raw.get("mem"),
        maxmem=raw.get("maxmem"),
        disk=raw.get("disk"),
        maxdisk=raw.get("maxdisk"),
        loadavg=loadavg,
    )


class ActionGuard:
    def __init__(self, protected: frozenset[tuple[str, int]]) -> None:
        self._protected = protected

    def is_protected(self, kind: GuestKind, vmid: int) -> bool:
        return (kind, vmid) in self._protected

    def assert_not_protected(self, kind: GuestKind, vmid: int) -> None:
        if self.is_protected(kind, vmid):
            raise ProtectedGuestError(kind, vmid)

    def assert_action_allowed(
        self,
        *,
        current: GuestStatus,
        action: PowerAction,
    ) -> None:
        if action == "start" and current == "running":
            raise AlreadyInStateError("running")
        if action == "resume" and current == "running":
            raise AlreadyInStateError("running")
        if action == "suspend" and current != "running":
            raise InvalidTransitionError(action, current)
        if action == "reboot" and current != "running":
            raise InvalidTransitionError(action, current)
        if action in ("stop", "shutdown") and current == "stopped":
            raise AlreadyInStateError("stopped")
        if action == "resume" and current != "paused":
            raise InvalidTransitionError(action, current)
        if action == "start" and current not in ("stopped", "unknown"):
            if current == "paused":
                raise InvalidTransitionError(action, current)


class ProtectedGuestError(Exception):
    def __init__(self, kind: GuestKind, vmid: int) -> None:
        super().__init__(f"protected guest {kind}:{vmid}")
        self.kind = kind
        self.vmid = vmid


class AlreadyInStateError(Exception):
    def __init__(self, state: str) -> None:
        super().__init__(state)
        self.state = state


class InvalidTransitionError(Exception):
    def __init__(self, action: PowerAction, current: GuestStatus) -> None:
        super().__init__(f"{action} from {current}")
        self.action = action
        self.current = current
