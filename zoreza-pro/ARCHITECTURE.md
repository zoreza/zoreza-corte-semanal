# Zoreza Pro — Arquitectura del Sistema

## Resumen Ejecutivo

**Zoreza Pro** es la evolución robusta del MVP "Zoreza · Corte Semanal". Mantiene toda la
lógica de negocio (cortes semanales, máquinas, contadores, gastos, tickets) y agrega:

| Capacidad | MVP (actual) | Zoreza Pro |
|-----------|-------------|------------|
| Base de datos | SQLite local | **PostgreSQL en servidor** |
| Offline | N/A | **SQLite local + sync automático** |
| API | Ninguna (Streamlit directo) | **REST API (FastAPI)** |
| Autenticación | Session cookie | **JWT con refresh tokens** |
| Frontend | Streamlit (Python) | **PWA (React) o App Android (Flutter)** |
| Multi-usuario simultáneo | No (SQLite lock) | **Sí (PostgreSQL + pool)** |
| Impresión térmica | HTML en navegador | **Bluetooth nativo (Flutter) o Web Bluetooth API** |
| Auditoría | Tabla edit_log básica | **Audit trail completo con sync_status** |
| Despliegue | Streamlit Cloud | **Docker Compose / Railway / AWS** |

---

## ¿Web PWA o App Android Nativa?

### Recomendación: **Flutter (Android prioritario) + FastAPI Backend**

| Criterio | PWA (React) | Flutter Android | Ganador |
|----------|-------------|-----------------|---------|
| Offline robusto | Service Workers + IndexedDB | SQLite nativo + WorkManager | **Flutter** |
| Impresión térmica Bluetooth | Web Bluetooth (limitado) | ESC/POS nativo | **Flutter** |
| Instalación | "Agregar a inicio" | Play Store / APK directo | **Flutter** |
| Actualizaciones | Instantáneas | Play Store review | PWA |
| Complejidad de desarrollo | Media | Media-Alta | Empate |
| Acceso sin internet | Bueno | **Excelente** | **Flutter** |
| Costo de desarrollo | Menor | Medio | PWA |

**Veredicto**: Para operadores de campo que recolectan efectivo de máquinas, necesitan
offline confiable y deben imprimir tickets térmicos por Bluetooth, **Flutter es superior**.
Sin embargo, el **backend FastAPI es idéntico** para ambos casos.

**Estrategia recomendada**:
1. **Fase 1**: Backend FastAPI + PostgreSQL (este proyecto)
2. **Fase 2a**: PWA React como frontend rápido para admins (dashboard web)
3. **Fase 2b**: App Flutter Android para operadores de campo

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────┐
│                    CLIENTES                          │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Flutter   │  │ PWA      │  │ Admin Dashboard  │  │
│  │ Android   │  │ React    │  │ (React/Web)      │  │
│  │ (Campo)   │  │ (Opcional│  │                  │  │
│  │           │  │          │  │                  │  │
│  │ SQLite    │  │IndexedDB │  │                  │  │
│  │ local     │  │ local    │  │                  │  │
│  └─────┬─────┘  └─────┬────┘  └────────┬─────────┘  │
│        │              │                │             │
└────────┼──────────────┼────────────────┼─────────────┘
         │              │                │
         ▼              ▼                ▼
    ┌─────────────────────────────────────────┐
    │           API Gateway / HTTPS            │
    │         (nginx / Traefik / ALB)          │
    └─────────────────────┬───────────────────┘
                          │
    ┌─────────────────────▼───────────────────┐
    │           FastAPI Backend                 │
    │                                          │
    │  ┌────────┐ ┌──────────┐ ┌───────────┐  │
    │  │ Auth   │ │ Cortes   │ │ Sync      │  │
    │  │ JWT    │ │ CRUD+Biz │ │ Engine    │  │
    │  ├────────┤ ├──────────┤ ├───────────┤  │
    │  │ RBAC   │ │ Gastos   │ │ Conflicts │  │
    │  │        │ │          │ │ Resolution│  │
    │  ├────────┤ ├──────────┤ ├───────────┤  │
    │  │ Export │ │ Dashboard│ │ Tickets   │  │
    │  │ CSV/PDF│ │ KPIs     │ │ HTML/ESC  │  │
    │  └────────┘ └──────────┘ └───────────┘  │
    │                                          │
    │         SQLAlchemy ORM + Alembic         │
    └─────────────────────┬───────────────────┘
                          │
    ┌─────────────────────▼───────────────────┐
    │          PostgreSQL 15+                   │
    │                                          │
    │  Tablas principales:                     │
    │  usuarios, clientes, rutas, maquinas,    │
    │  cortes, corte_detalle, gastos,          │
    │  notifications, audit_log, sync_log,     │
    │  catalogs (irregularidad, omision,       │
    │  evento_contador)                        │
    └──────────────────────────────────────────┘
```

---

## Protocolo de Sincronización Offline

### Estrategia: "Offline-First with Server Authority"

```
┌──────────────────────────────────────────────┐
│                FLUJO DE SYNC                  │
│                                              │
│  1. App arranca → checa conectividad         │
│  2. Si ONLINE:                               │
│     a. Pull: GET /api/v1/sync/pull?since=X   │
│        → Recibe cambios del servidor          │
│        → Aplica a SQLite local               │
│     b. Push: POST /api/v1/sync/push          │
│        → Envía cambios locales pendientes    │
│        → Servidor resuelve conflictos        │
│        → Respuesta con IDs definitivos       │
│  3. Si OFFLINE:                              │
│     a. Trabaja contra SQLite local           │
│     b. Marca registros como pending_sync     │
│     c. Cuando recupere internet → paso 2     │
│                                              │
│  Resolución de conflictos:                   │
│  - "Last write wins" para datos simples      │
│  - "Server wins" para cortes CERRADOS        │
│  - UUIDs para evitar colisión de IDs         │
└──────────────────────────────────────────────┘
```

### Campos de sincronización en cada tabla:

```sql
uuid          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
sync_status   TEXT DEFAULT 'synced',  -- 'synced', 'pending', 'conflict'
sync_version  BIGINT DEFAULT 0,       -- Incrementa con cada cambio
updated_at    TIMESTAMPTZ,            -- Para detectar conflictos
device_id     TEXT,                    -- Identificador del dispositivo
```

---

## Stack Tecnológico

### Backend
- **Python 3.11+**
- **FastAPI** — Framework async de alto rendimiento
- **SQLAlchemy 2.0** — ORM con soporte async
- **Alembic** — Migraciones de base de datos
- **PostgreSQL 15+** — BD principal en servidor
- **Pydantic v2** — Validación de datos
- **python-jose** — JWT tokens
- **passlib[bcrypt]** — Hashing de contraseñas
- **uvicorn** — Servidor ASGI
- **Docker** — Contenedorización

### Frontend (Flutter — Fase 2b)
- **Flutter 3.x** — Framework cross-platform
- **sqflite** — SQLite local para offline
- **dio** — HTTP client
- **riverpod** — State management
- **esc_pos_bluetooth** — Impresión térmica
- **connectivity_plus** — Detección de red

### Frontend (PWA React — Fase 2a)
- **React 18** + **TypeScript**
- **Vite** — Build tool
- **TanStack Query** — Data fetching + cache
- **Dexie.js** — IndexedDB wrapper
- **Workbox** — Service Worker
- **Tailwind CSS** — Estilos
