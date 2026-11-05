from __future__ import annotations

from services.guard import node_from_raw, normalize_node_status_raw


def test_normalize_node_status_raw_pve9_nested() -> None:
    raw = {
        "node": "dusha",
        "uptime": 100,
        "cpu": 0,
        "memory": {"used": 3, "total": 10, "available": 7, "free": 5},
        "rootfs": {"used": 1, "total": 100, "avail": 99, "free": 99},
        "cpuinfo": {"cpus": 20, "cores": 12},
        "loadavg": [0.1, 0.2, 0.3],
    }
    normalized = normalize_node_status_raw(raw)
    assert normalized["mem"] == 3
    assert normalized["maxmem"] == 10
    assert normalized["disk"] == 1
    assert normalized["maxdisk"] == 100
    assert normalized["maxcpu"] == 20

    node = node_from_raw(raw)
    assert node.mem == 3
    assert node.maxmem == 10
    assert node.disk == 1
    assert node.maxdisk == 100
    assert node.maxcpu == 20
