"""Config endpoints — global settings (key/value) + logo upload."""

from __future__ import annotations

import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.models.config import Config
from app.schemas.config import ConfigItem, ConfigUpdate
from sqlalchemy import select

router = APIRouter()

LOGO_DIR = Path("data/uploads")
LOGO_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=list[ConfigItem])
async def list_all_config(db: DbSession, user: CurrentUser):
    result = await db.execute(select(Config).order_by(Config.key))
    return list(result.scalars().all())


@router.get("/{key}", response_model=ConfigItem)
async def get_config(key: str, db: DbSession, user: CurrentUser):
    result = await db.execute(select(Config).where(Config.key == key))
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Config '{key}' no encontrada")
    return obj


@router.put("/{key}", response_model=ConfigItem)
async def set_config(key: str, body: ConfigUpdate, db: DbSession, admin: AdminUser):
    result = await db.execute(select(Config).where(Config.key == key))
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = Config(key=key, value=body.value, updated_by=admin.uuid)
        db.add(obj)
    else:
        obj.value = body.value
        obj.updated_by = admin.uuid
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{key}", status_code=204)
async def delete_config(key: str, db: DbSession, _admin: AdminUser):
    result = await db.execute(select(Config).where(Config.key == key))
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await db.delete(obj)
    await db.commit()


@router.post("/logo/upload")
async def upload_logo(file: UploadFile, db: DbSession, admin: AdminUser):
    if file.content_type not in ("image/png", "image/jpeg", "image/webp"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Solo PNG, JPEG o WEBP")
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Máximo 2MB")

    # Store as base64 in config for simplicity (portable, no file serving needed)
    b64 = base64.b64encode(contents).decode()
    data_uri = f"data:{file.content_type};base64,{b64}"

    result = await db.execute(select(Config).where(Config.key == "logo"))
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = Config(key="logo", value=data_uri, updated_by=admin.uuid)
        db.add(obj)
    else:
        obj.value = data_uri
        obj.updated_by = admin.uuid
    await db.commit()
    await db.refresh(obj)
    return {"message": "Logo actualizado", "key": "logo"}
