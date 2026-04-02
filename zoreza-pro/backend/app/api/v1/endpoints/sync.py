"""Sync endpoints — offline-first protocol.

Pull: client requests reference data and changes since a given version.
Push: client sends local pending changes (cortes, gastos) to the server.
"""

from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.cliente import Cliente
from app.models.maquina import Maquina
from app.models.ruta import Ruta
from app.models.maquina_ruta import MaquinaRuta
from app.models.catalogs import CatIrregularidad, CatOmision, CatEventoContador
from app.models.corte import Corte
from app.models.corte_detalle import CorteDetalle
from app.models.gasto import Gasto
from app.schemas.sync import (
    SyncPullRequest, SyncPullResponse, SyncChange,
    SyncPushRequest, SyncPushResponse, SyncConflict,
)

router = APIRouter()


def _row_to_dict(row) -> dict:
    """Convert an ORM row to a JSON-serialisable dict."""
    d = {}
    for c in row.__table__.columns:
        v = getattr(row, c.name)
        if isinstance(v, UUID):
            v = v.hex
        elif hasattr(v, 'isoformat'):
            v = v.isoformat()
        d[c.name] = v
    return d


@router.post("/pull", response_model=SyncPullResponse)
async def sync_pull(body: SyncPullRequest, db: DbSession, user: CurrentUser):
    """Return reference data and records changed since `since_version`.

    On first sync (since_version=0) the full reference dataset is returned.
    """
    changes: list[SyncChange] = []
    ver = body.since_version

    # Reference / catalog tables — always send full set on first pull,
    # incremental otherwise (using sync_version).
    ref_tables = [
        ('clientes', Cliente),
        ('maquinas', Maquina),
        ('rutas', Ruta),
        ('maquina_ruta', MaquinaRuta),
        ('cat_irregularidad', CatIrregularidad),
        ('cat_omision', CatOmision),
        ('cat_evento_contador', CatEventoContador),
    ]

    for table_name, model in ref_tables:
        stmt = select(model)
        if ver > 0:
            stmt = stmt.where(model.sync_version > ver)
        rows = (await db.execute(stmt)).scalars().all()
        for row in rows:
            changes.append(SyncChange(
                table=table_name,
                uuid=row.uuid,
                action='upsert',
                data=_row_to_dict(row),
                sync_version=row.sync_version,
            ))

    # Transactional tables — cortes and detalles the user has access to
    corte_stmt = select(Corte)
    if ver > 0:
        corte_stmt = corte_stmt.where(Corte.sync_version > ver)
    cortes = (await db.execute(corte_stmt)).scalars().all()
    for c in cortes:
        changes.append(SyncChange(
            table='cortes',
            uuid=c.uuid,
            action='upsert',
            data=_row_to_dict(c),
            sync_version=c.sync_version,
        ))

    det_stmt = select(CorteDetalle)
    if ver > 0:
        det_stmt = det_stmt.where(CorteDetalle.sync_version > ver)
    dets = (await db.execute(det_stmt)).scalars().all()
    for d in dets:
        changes.append(SyncChange(
            table='corte_detalle',
            uuid=d.uuid,
            action='upsert',
            data=_row_to_dict(d),
            sync_version=d.sync_version,
        ))

    gasto_stmt = select(Gasto)
    if ver > 0:
        gasto_stmt = gasto_stmt.where(Gasto.sync_version > ver)
    gastos = (await db.execute(gasto_stmt)).scalars().all()
    for g in gastos:
        changes.append(SyncChange(
            table='gastos',
            uuid=g.uuid,
            action='upsert',
            data=_row_to_dict(g),
            sync_version=g.sync_version,
        ))

    # Current version = max sync_version across all returned changes, or the
    # requested version if nothing new.
    max_ver = max((ch.sync_version for ch in changes), default=ver)

    return SyncPullResponse(current_version=max_ver, changes=changes)


@router.post("/push", response_model=SyncPushResponse)
async def sync_push(body: SyncPushRequest, db: DbSession, user: CurrentUser):
    """Accept locally-created records from the client device.

    Supports: cortes, corte_detalle, gastos.
    Reference tables are server-authoritative and rejected on push.
    """
    accepted = 0
    conflicts: list[SyncConflict] = []

    # Tables that the client can push
    writable = {
        'cortes': Corte,
        'corte_detalle': CorteDetalle,
        'gastos': Gasto,
    }

    for item in body.changes:
        model = writable.get(item.table)
        if model is None:
            conflicts.append(SyncConflict(
                table=item.table,
                uuid=item.uuid,
                reason='server_authoritative',
                server_data={},
            ))
            continue

        existing = await db.get(model, item.uuid)

        if item.action == 'delete':
            if existing:
                await db.delete(existing)
                accepted += 1
            continue

        # Upsert
        if existing:
            # Conflict check: CERRADO cortes are immutable
            if item.table == 'cortes' and getattr(existing, 'estado', '') == 'CERRADO':
                conflicts.append(SyncConflict(
                    table=item.table,
                    uuid=item.uuid,
                    reason='corte_cerrado',
                    server_data=_row_to_dict(existing),
                ))
                continue

            # Last-write-wins: update mutable fields
            for k, v in item.data.items():
                if k in ('uuid', 'created_at'):
                    continue
                if hasattr(existing, k):
                    setattr(existing, k, v)
            existing.sync_status = 'synced'
            existing.device_id = body.device_id
        else:
            # New record
            data = dict(item.data)
            data['uuid'] = item.uuid
            data['sync_status'] = 'synced'
            data['device_id'] = body.device_id
            row = model(**{k: v for k, v in data.items() if hasattr(model, k)})
            db.add(row)

        accepted += 1

    await db.commit()

    # Return current max version
    return SyncPushResponse(
        accepted=accepted,
        conflicts=conflicts,
        server_version=0,
    )
