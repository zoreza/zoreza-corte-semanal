"""Catalog endpoints (irregularidad, omision, evento_contador)."""

from uuid import UUID

from fastapi import APIRouter

from app.core.deps import AdminUser, CurrentUser, DbSession
from app.schemas.catalog import CatalogItemCreate, CatalogItemOut, CatalogItemUpdate
from app.services.crud_service import list_catalog, upsert_catalog

router = APIRouter()


@router.get("/{catalog}", response_model=list[CatalogItemOut])
async def list_catalog_items(
    catalog: str, db: DbSession, user: CurrentUser, activo: bool | None = None
):
    return await list_catalog(db, catalog, activo=activo)


@router.post("/{catalog}", response_model=CatalogItemOut, status_code=201)
async def create_catalog_item(
    catalog: str, body: CatalogItemCreate, db: DbSession, _admin: AdminUser
):
    return await upsert_catalog(db, catalog, None, body.model_dump())


@router.patch("/{catalog}/{item_id}", response_model=CatalogItemOut)
async def update_catalog_item(
    catalog: str, item_id: UUID, body: CatalogItemUpdate, db: DbSession, _admin: AdminUser
):
    return await upsert_catalog(db, catalog, item_id, body.model_dump(exclude_unset=True))
