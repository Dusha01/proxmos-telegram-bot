from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class AdminCreate(BaseModel):
    user_id: int
    chat_id: int
    name: str | None = None


class AdminOut(BaseModel):
    user_id: int
    chat_id: int
    name: str | None = None
    active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminDocument(BaseModel):
    user_id: int
    chat_id: int
    name: str | None = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
