from __future__ import annotations

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from db.models.dto import AdminCreate, AdminDocument, AdminOut


class AdminRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db["admins"]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index(
            [("user_id", 1), ("chat_id", 1)],
            unique=True,
            name="user_chat_unique",
        )

    async def create(self, payload: AdminCreate) -> AdminOut:
        doc = AdminDocument(
            user_id=payload.user_id,
            chat_id=payload.chat_id,
            name=payload.name,
            created_at=datetime.now(UTC),
        )
        data = doc.model_dump()
        try:
            await self._collection.insert_one(data)
        except DuplicateKeyError as exc:
            raise AdminAlreadyExistsError from exc
        return AdminOut(**_strip_id(data))

    async def find_active(self, user_id: int, chat_id: int) -> AdminOut | None:
        raw = await self._collection.find_one(
            {"user_id": user_id, "chat_id": chat_id, "active": True}
        )
        if raw is None:
            return None
        return AdminOut(**_strip_id(raw))


def _strip_id(document: dict) -> dict:
    return {key: value for key, value in document.items() if key != "_id"}


class AdminAlreadyExistsError(Exception):
    pass


def create_motor_client(mongo_url: str) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(mongo_url)
