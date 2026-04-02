"""V1 router — mounts all sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, clientes, config, cortes, dashboard, gastos, maquinas, rutas, usuarios, catalogs, sync

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
router.include_router(maquinas.router, prefix="/maquinas", tags=["Máquinas"])
router.include_router(rutas.router, prefix="/rutas", tags=["Rutas"])
router.include_router(cortes.router, prefix="/cortes", tags=["Cortes"])
router.include_router(gastos.router, prefix="/gastos", tags=["Gastos"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(catalogs.router, prefix="/catalogs", tags=["Catálogos"])
router.include_router(config.router, prefix="/config", tags=["Configuración"])
router.include_router(sync.router, prefix="/sync", tags=["Sincronización"])
