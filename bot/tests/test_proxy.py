from __future__ import annotations

import pytest

from core.proxy import _mask_proxy_url, normalize_proxy_url


@pytest.mark.parametrize(
    "value",
    ["", "none", "NULL", "-", "off", "false"],
)
def test_normalize_proxy_empty_values(value: str) -> None:
    assert normalize_proxy_url(value) is None


def test_normalize_proxy_keeps_url() -> None:
    assert normalize_proxy_url("http://proxy:3128") == "http://proxy:3128"


def test_mask_proxy_hides_password() -> None:
    masked = _mask_proxy_url("http://user:secret@proxy:3128")
    assert "secret" not in masked
    assert "user:***" in masked
