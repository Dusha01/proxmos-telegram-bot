from __future__ import annotations

import pytest

from services.guard import (
    ActionGuard,
    AlreadyInStateError,
    InvalidTransitionError,
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


def test_reboot_from_running_allowed() -> None:
    guard = ActionGuard(frozenset())
    guard.assert_action_allowed(current="running", action="reboot")


def test_reboot_from_stopped_rejected() -> None:
    guard = ActionGuard(frozenset())
    with pytest.raises(InvalidTransitionError):
        guard.assert_action_allowed(current="stopped", action="reboot")
