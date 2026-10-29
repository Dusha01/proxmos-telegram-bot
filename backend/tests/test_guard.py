from __future__ import annotations

import pytest

from services.guard import (
    ActionGuard,
    AlreadyInStateError,
    ProtectedGuestError,
)


def test_protected_guest_blocked() -> None:
    guard = ActionGuard(frozenset({("lxc", 100)}))
    with pytest.raises(ProtectedGuestError):
        guard.assert_not_protected("lxc", 100)


def test_already_running_start() -> None:
    guard = ActionGuard(frozenset())
    with pytest.raises(AlreadyInStateError):
        guard.assert_action_allowed(current="running", action="start")
