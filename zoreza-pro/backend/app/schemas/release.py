"""Schemas for app releases (APK distribution)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReleaseOut(BaseModel):
    uuid: str
    version_name: str
    version_code: int
    filename: str
    file_size: int
    release_notes: str | None
    is_mandatory: bool
    activo: bool
    download_url: str
    created_at: str

    model_config = {"from_attributes": True}


class ReleaseLatest(BaseModel):
    """Response for the public version-check endpoint."""
    version_name: str
    version_code: int
    release_notes: str | None
    is_mandatory: bool
    download_url: str


class ReleaseCreate(BaseModel):
    version_name: str = Field(..., min_length=1, max_length=30, pattern=r"^\d+\.\d+\.\d+$")
    version_code: int = Field(..., ge=1)
    release_notes: str | None = None
    is_mandatory: bool = False
