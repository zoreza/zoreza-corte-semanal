"""Sync protocol schemas — offline-first sync."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class SyncPullRequest(BaseModel):
    """Client asks for changes since a given sync_version."""

    since_version: int = 0
    device_id: str


class SyncPullResponse(BaseModel):
    """Server returns changed records since the requested version."""

    current_version: int
    changes: list[SyncChange]


class SyncChange(BaseModel):
    table: str
    uuid: UUID
    action: str  # "upsert" | "delete"
    data: dict[str, Any]
    sync_version: int


class SyncPushRequest(BaseModel):
    """Client pushes local pending changes to server."""

    device_id: str
    changes: list[SyncPushItem]


class SyncPushItem(BaseModel):
    table: str
    uuid: UUID
    action: str  # "upsert" | "delete"
    data: dict[str, Any]
    local_updated_at: datetime


class SyncPushResponse(BaseModel):
    accepted: int
    conflicts: list[SyncConflict]
    server_version: int


class SyncConflict(BaseModel):
    table: str
    uuid: UUID
    reason: str
    server_data: dict[str, Any]
