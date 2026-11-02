from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from db.models.dto import AdminOut
from db.repositories.repo import AdminRepository


@pytest.fixture
def admin_repo() -> AdminRepository:
    mock_collection = AsyncMock()
    mock_db = MagicMock()
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    repo = AdminRepository(mock_db)
    repo._collection = mock_collection
    return repo


@pytest.mark.asyncio
async def test_ensure_trusted_admin_upserts_unique_chat_ids(admin_repo: AdminRepository) -> None:
    await admin_repo.ensure_trusted_admin(42, [-100, 42, -100], "admin")
    assert admin_repo._collection.update_one.await_count == 2
    calls = admin_repo._collection.update_one.await_args_list
    chat_ids = {call.args[0]["chat_id"] for call in calls}
    assert chat_ids == {-100, 42}


@pytest.mark.asyncio
async def test_find_active_returns_match(admin_repo: AdminRepository) -> None:
    admin_repo._collection.find_one = AsyncMock(
        return_value={
            "user_id": 1,
            "chat_id": -100,
            "name": "a",
            "active": True,
            "created_at": datetime.now(UTC),
        }
    )
    result = await admin_repo.find_active(1, -100)
    assert result is not None
    assert result.chat_id == -100
