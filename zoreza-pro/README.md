# Zoreza Pro

**Sistema robusto de cortes semanales para operadores de máquinas recreativas y vending.**

Evolución del MVP "Zoreza · Corte Semanal" con:
- Base de datos PostgreSQL en servidor
- API REST con FastAPI
- Autenticación JWT
- Soporte offline-first con sincronización
- Preparado para frontend PWA (web) y Flutter (Android)

---

## Inicio Rápido

### Opción 1: Docker Compose (recomendado)

```bash
cd zoreza-pro

# Copiar y editar variables de entorno
cp backend/.env.example backend/.env
# Editar SECRET_KEY con: openssl rand -hex 64

# Levantar PostgreSQL + Backend
docker compose up -d

# Ejecutar seed (datos iniciales)
docker compose exec backend python -m app.seed

# API disponible en: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Opción 2: Desarrollo local

```bash
cd zoreza-pro/backend

# Crear entorno virtual
python3 -m venv .venv && source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Asegurar que PostgreSQL esté corriendo (local o Docker)
# Copiar .env.example a .env y ajustar DATABASE_URL

# Crear tablas y datos iniciales
python -m app.seed

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

---

## Estructura del Proyecto

```
zoreza-pro/
├── ARCHITECTURE.md          # Arquitectura detallada del sistema
├── docker-compose.yml       # PostgreSQL + Backend
│
├── backend/                 # ── FastAPI Backend ──
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini          # Migraciones de BD
│   ├── migrations/          # Alembic migrations
│   │
│   ├── app/
│   │   ├── main.py          # Entry point FastAPI
│   │   ├── seed.py          # Datos iniciales
│   │   │
│   │   ├── core/            # Configuración y seguridad
│   │   │   ├── config.py    # Settings (env vars)
│   │   │   ├── security.py  # JWT + bcrypt
│   │   │   └── deps.py      # Dependencies (DB, auth, roles)
│   │   │
│   │   ├── db/              # Capa de datos
│   │   │   ├── base.py      # Base ORM (UUID, sync, timestamps)
│   │   │   └── session.py   # Async engine + session factory
│   │   │
│   │   ├── models/          # SQLAlchemy ORM models
│   │   │   ├── usuario.py
│   │   │   ├── cliente.py
│   │   │   ├── ruta.py
│   │   │   ├── maquina.py
│   │   │   ├── corte.py
│   │   │   ├── corte_detalle.py
│   │   │   ├── gasto.py
│   │   │   ├── catalogs.py  # irregularidad, omision, evento_contador
│   │   │   ├── notification.py
│   │   │   ├── audit_log.py
│   │   │   ├── config.py
│   │   │   ├── usuario_ruta.py
│   │   │   └── maquina_ruta.py
│   │   │
│   │   ├── schemas/         # Pydantic v2 schemas
│   │   │   ├── auth.py
│   │   │   ├── usuario.py
│   │   │   ├── cliente.py
│   │   │   ├── maquina.py
│   │   │   ├── ruta.py
│   │   │   ├── corte.py     # Corte + CorteDetalle
│   │   │   ├── gasto.py
│   │   │   ├── catalog.py
│   │   │   ├── dashboard.py
│   │   │   └── sync.py      # Protocolo de sincronización
│   │   │
│   │   ├── services/        # Lógica de negocio
│   │   │   ├── auth_service.py
│   │   │   ├── usuario_service.py
│   │   │   ├── rbac_service.py
│   │   │   ├── corte_service.py
│   │   │   ├── crud_service.py
│   │   │   └── dashboard_service.py
│   │   │
│   │   └── api/v1/          # Endpoints REST
│   │       ├── router.py    # Monta todos los sub-routers
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── usuarios.py
│   │           ├── clientes.py
│   │           ├── maquinas.py
│   │           ├── rutas.py
│   │           ├── cortes.py
│   │           ├── gastos.py
│   │           ├── dashboard.py
│   │           ├── catalogs.py
│   │           └── sync.py
│   │
│   └── tests/
│       └── test_basic.py
│
├── frontend/                # ── Placeholder para PWA React ──
│   └── src/
│
└── docs/
    └── FLUTTER_APP.md       # Guía para la app Flutter Android
```

---

## API Endpoints

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | Login → tokens JWT |
| POST | `/api/v1/auth/refresh` | Renovar access token |
| GET | `/api/v1/auth/me` | Info del usuario actual |

### Cortes (flujo principal)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/cortes` | Listar cortes (filtros: cliente, estado) |
| POST | `/api/v1/cortes` | Crear/obtener borrador |
| GET | `/api/v1/cortes/{id}` | Detalle del corte |
| GET | `/api/v1/cortes/{id}/detalles` | Detalle por máquina |
| POST | `/api/v1/cortes/{id}/detalle/capturada` | Guardar máquina capturada |
| POST | `/api/v1/cortes/{id}/detalle/omitida` | Guardar máquina omitida |
| POST | `/api/v1/cortes/{id}/close` | Cerrar corte |
| POST | `/api/v1/cortes/{id}/reopen` | Reabrir (SUPERVISOR+) |
| GET | `/api/v1/cortes/{id}/audit-log` | Historial de ediciones |

### CRUD Admin
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET/POST/PATCH | `/api/v1/usuarios` | Gestión de usuarios |
| GET/POST/PATCH | `/api/v1/clientes` | Gestión de clientes |
| GET/POST/PATCH | `/api/v1/maquinas` | Gestión de máquinas |
| GET/POST/PATCH | `/api/v1/rutas` | Gestión de rutas |
| GET/POST/DELETE | `/api/v1/gastos` | Gestión de gastos |
| GET | `/api/v1/gastos/summary` | Resumen de gastos |
| GET/POST/PATCH | `/api/v1/catalogs/{tipo}` | Catálogos |

### Dashboard & Sync
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/dashboard/summary` | KPIs del dashboard |
| POST | `/api/v1/sync/pull` | Pull cambios (offline sync) |
| POST | `/api/v1/sync/push` | Push cambios locales |

---

## Usuarios por defecto

| Usuario | Password | Rol |
|---------|----------|-----|
| admin | admin123 | ADMIN |
| operador | operador123 | OPERADOR |

⚠️ **Cambiar contraseñas en producción.**

---

## Migraciones de BD

```bash
# Generar nueva migración
cd backend
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

---

## Siguiente paso: App Android (Flutter)

Ver [docs/FLUTTER_APP.md](docs/FLUTTER_APP.md) para la guía completa de implementación
de la app móvil con soporte offline y sincronización.
