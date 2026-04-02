# Zoreza Pro — Documento Técnico para Continuidad de Desarrollo

> Este archivo está diseñado para que otro modelo de IA (o desarrollador) pueda entender
> completamente el proyecto y continuar su desarrollo sin ambigüedad.

## 1. Visión General

**Zoreza Pro** es un sistema multi-tenant de corte semanal para negocios de máquinas de
vending y arcade. Permite a operadores de campo capturar la recaudación de cada máquina,
registrar gastos, imprimir tickets térmicos y sincronizar datos offline-first.

### Stack Tecnológico

| Componente | Tecnología | Ubicación |
|-----------|-----------|-----------|
| Backend API | FastAPI + SQLAlchemy 2.0 async + aiosqlite | `backend/` |
| App Android | Flutter 3.41.6 + Dart 3.11.4 + Riverpod | `app/` |
| Web Admin | React 19 + Vite 8.0.3 + react-router-dom v7 | `web/` |
| Base de Datos | SQLite (una BD por tenant + una BD maestra) | `data/` en runtime |
| Autenticación | JWT (access 60min + refresh 30 días) | Backend |
| Impresión | ESC/POS Bluetooth nativo (Flutter) | App Android |

### Arquitectura Multi-Tenant

```
Petición HTTP
    │
    ▼
/{slug}/api/v1/...          ← URL con slug del tenant
    │
    ▼
TenantMiddleware            ← Extrae slug, busca tenant en master.db
    │
    ▼
get_tenant_session()        ← Crea sesión async a data/tenants/{slug}.db
    │
    ▼
Endpoint (inyección de dependencias con Depends)
```

- **Master DB** (`data/master.db`): Tablas `tenants`, `super_admins`, `app_releases`
- **Tenant DB** (`data/tenants/{slug}.db`): Esquema completo aislado por tenant

El Super Admin accede vía `/zoreza-admin/api/...` (ruta separada, sin middleware de tenant).

---

## 2. Base de Datos — Modelos Completos

### 2.1 Master DB (tenant.py, app_release.py)

Todos los modelos heredan de `Base` con columnas automáticas: `uuid` (PK, UUID4), `created_at`, `updated_at`.

**Tenant**
| Columna | Tipo | Notas |
|---------|------|-------|
| slug | String(50) | unique, indexed |
| nombre | String(200) | |
| contacto_nombre | String(200) | nullable |
| contacto_email | String(200) | nullable |
| contacto_telefono | String(30) | nullable |
| plan | String(30) | default="basico" |
| activo | Boolean | default=True |
| notas | Text | nullable |

**SuperAdmin**
| Columna | Tipo | Notas |
|---------|------|-------|
| username | String(50) | unique |
| password_hash | String(255) | |
| nombre | String(150) | |
| activo | Boolean | default=True |

**AppRelease**
| Columna | Tipo | Notas |
|---------|------|-------|
| version_name | String(30) | ej: "1.2.0" |
| version_code | Integer | ej: 3 (para comparación numérica) |
| filename | String(255) | nombre del archivo APK |
| file_size | Integer | default=0, bytes |
| release_notes | Text | nullable |
| is_mandatory | Boolean | default=False |
| activo | Boolean | default=True |

### 2.2 Tenant DB

**Usuario**
| Columna | Tipo | Constraint |
|---------|------|-----------|
| username | String(50) | unique |
| password_hash | String(255) | |
| nombre | String(150) | |
| telefono | String(30) | default="" |
| email | String(200) | default="" |
| rol | String(20) | CHECK IN ('ADMIN','SUPERVISOR','OPERADOR') |
| activo | Boolean | default=True |

**Cliente** (dueño de establecimiento con máquinas)
| Columna | Tipo | Notas |
|---------|------|-------|
| nombre | String(200) | |
| telefono | String(30) | default="" |
| email | String(200) | nullable |
| direccion_postal | String(400) | nullable |
| comision_pct | Float | default=0.40 (40%) |
| activo | Boolean | default=True |

**Maquina**
| Columna | Tipo | Notas |
|---------|------|-------|
| codigo | String(50) | unique |
| fondo | Float | default=0.0 |
| cliente_id | UUID FK→clientes | nullable |
| activo | Boolean | default=True |

**Ruta**
| Columna | Tipo | Notas |
|---------|------|-------|
| nombre | String(100) | unique |
| descripcion | Text | nullable |
| activo | Boolean | default=True |

Relación M:N `ruta_maquina` (tabla asociativa) vincula rutas con máquinas.

**Corte** (corte semanal por cliente)
| Columna | Tipo | Notas |
|---------|------|-------|
| cliente_id | UUID FK→clientes | |
| week_start | Date | |
| week_end | Date | |
| fecha_corte | Date | nullable |
| comision_pct_usada | Float | default=0.0 |
| neto_cliente | Float | default=0.0 |
| pago_cliente | Float | default=0.0 |
| ganancia_dueno | Float | default=0.0 |
| estado | String(20) | CHECK IN ('BORRADOR','CERRADO'), default='BORRADOR' |
| created_by | UUID FK→usuarios | nullable |

Constraint: UNIQUE(cliente_id, week_start)

**CorteDetalle** (una fila por máquina capturada en un corte)
| Columna | Tipo | Notas |
|---------|------|-------|
| corte_id | UUID FK→cortes (CASCADE) | |
| maquina_id | UUID FK→maquinas | |
| estado_maquina | String(20) | CHECK IN ('CAPTURADA','OMITIDA') |
| score_tarjeta | Float | nullable |
| efectivo_total | Float | nullable |
| fondo | Float | nullable |
| recaudable | Float | nullable (calculado) |
| diferencia_score | Float | nullable (calculado) |
| contador_entrada_actual | Integer | nullable |
| contador_salida_actual | Integer | nullable |
| contador_entrada_prev | Integer | nullable |
| contador_salida_prev | Integer | nullable |
| delta_entrada | Integer | nullable (calculado) |
| delta_salida | Integer | nullable (calculado) |
| monto_estimado_contadores | Float | nullable (calculado) |
| causa_irregularidad_id | UUID FK→cat_irregularidad | nullable |
| nota_irregularidad | Text | nullable |
| evento_contador_id | UUID FK→cat_evento_contador | nullable |
| nota_evento_contador | Text | nullable |
| motivo_omision_id | UUID FK→cat_omision | nullable |
| nota_omision | Text | nullable |
| created_by | UUID FK→usuarios | nullable |

Constraint: UNIQUE(corte_id, maquina_id)

**Gasto**
| Columna | Tipo | Notas |
|---------|------|-------|
| fecha | Date | |
| categoria | String(30) | REFACCIONES, FONDOS_ROBOS, PERMISOS, EMPLEADOS, SERVICIOS, TRANSPORTE, OTRO |
| descripcion | String(200) | |
| monto | Float | |
| notas | Text | nullable |
| created_by | UUID FK→usuarios | nullable |

**Catálogos** (tablas dinámicas para dropdowns):
- `cat_irregularidad` — causas de irregularidad (nombre, activo)
- `cat_omision` — motivos de omisión de máquina (nombre, activo)
- `cat_evento_contador` — eventos de contador (nombre, activo)

---

## 3. API Backend — Endpoints Completos

### 3.1 Configuración Global (`backend/app/core/config.py`)

```python
app_tz = "America/Mexico_City"
api_v1_prefix = "/api/v1"
secret_key = "CHANGE-ME-in-production"
algorithm = "HS256"
access_token_expire_minutes = 60
refresh_token_expire_days = 30
default_tolerancia_pesos = 30.0
default_fondo_sugerido = 500.0
default_comision_pct = 0.40
```

### 3.2 Rutas de Tenant (`/{slug}/api/v1/...`)

**Autenticación** (`/auth`)
| Método | Ruta | Descripción |
|--------|------|------------|
| POST | /auth/login | Login → {access_token, refresh_token, token_type} |
| POST | /auth/refresh | Refresh token → nuevo access_token |
| GET | /auth/me | Info del usuario autenticado |

**Usuarios** (`/usuarios`) — Requiere rol ADMIN
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /usuarios | Listar usuarios (filtro ?activo=) |
| POST | /usuarios | Crear usuario |
| PUT | /usuarios/{id} | Actualizar usuario |

**Clientes** (`/clientes`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /clientes | Listar clientes (filtro ?activo=) |
| POST | /clientes | Crear cliente |
| PUT | /clientes/{id} | Actualizar cliente |

**Máquinas** (`/maquinas`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /maquinas | Listar máquinas (?cliente_id=, ?activo=) |
| POST | /maquinas | Crear máquina |
| PUT | /maquinas/{id} | Actualizar máquina |

**Rutas** (`/rutas`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /rutas | Listar rutas (?activo=) |
| POST | /rutas | Crear ruta |
| PUT | /rutas/{id} | Actualizar ruta |
| GET | /rutas/{id}/maquinas | Máquinas asignadas a ruta |
| POST | /rutas/{id}/maquinas/{maq_id} | Asignar máquina a ruta |
| DELETE | /rutas/{id}/maquinas/{maq_id} | Desasignar máquina |

**Cortes** (`/cortes`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /cortes | Listar cortes (?cliente_id=, ?estado=, ?limit=, ?offset=) |
| POST | /cortes | Crear corte (cliente_id, fecha_corte) |
| GET | /cortes/{id} | Detalle de corte |
| GET | /cortes/{id}/detalles | Detalles (máquinas) del corte |
| POST | /cortes/{id}/capture | Capturar máquina en corte |
| POST | /cortes/{id}/omit | Omitir máquina en corte |
| POST | /cortes/{id}/close | Cerrar corte (cambia estado a CERRADO, calcula totales) |

**Gastos** (`/gastos`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /gastos | Listar gastos (?fecha_inicio=, ?fecha_fin=, ?categoria=) |
| POST | /gastos | Crear gasto |
| DELETE | /gastos/{id} | Eliminar gasto |

**Dashboard** (`/dashboard`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /dashboard | Resumen: total recaudado, gastos, neto, por categoría, tendencias |

**Catálogos** (`/catalogs`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /catalogs/{type} | Listar items (type: irregularidad, omision, evento_contador) |
| POST | /catalogs/{type} | Crear item |
| PUT | /catalogs/{type}/{id} | Actualizar item |

**Configuración** (`/config`)
| Método | Ruta | Descripción |
|--------|------|------------|
| GET | /config | Listar todas las config |
| GET | /config/{key} | Obtener config por clave |
| PUT | /config/{key} | Establecer config |
| DELETE | /config/{key} | Eliminar config |
| POST | /config/logo | Subir logo del tenant |

**Sync** (`/sync`)
| Método | Ruta | Descripción |
|--------|------|------------|
| POST | /sync/pull | Pull cambios desde server (since_version, device_id) |
| POST | /sync/push | Push cambios locales al server (device_id, changes[]) |

### 3.3 Rutas de Super Admin (`/zoreza-admin/api/...`)

| Método | Ruta | Descripción |
|--------|------|------------|
| POST | /auth/login | Login super admin → tokens |
| GET | /auth/me | Info del super admin |
| GET | /tenants | Listar todos los tenants |
| POST | /tenants | Crear tenant (crea BD aislada + admin default) |
| GET | /tenants/{slug} | Detalle de tenant |
| PUT | /tenants/{slug} | Actualizar tenant |
| POST | /tenants/{slug}/reset-password | Resetear password del admin del tenant |
| GET | /releases | Listar releases de APK |
| POST | /releases | Subir nueva release (multipart: file + metadata) |
| GET | /releases/latest | Última release activa (para auto-update) |
| DELETE | /releases/{id} | Eliminar release |
| GET | /releases/{id}/download | Descargar APK |

---

## 4. Lógica de Negocio

### 4.1 Corte Semanal — Flujo Completo

1. **Crear corte**: Se selecciona un cliente y la fecha. El backend calcula `week_start` (lunes) y `week_end` (domingo) automáticamente basado en la fecha.
2. **Capturar máquinas**: El operador visita cada máquina del cliente y registra:
   - `efectivo_total` — dinero encontrado en la máquina
   - `score_tarjeta` — lectura del score electrónico
   - `fondo` — dinero que se deja como fondo operativo
   - Contadores (entrada/salida actual)
3. **Cálculos automáticos** (en captura):
   - `recaudable = efectivo_total - fondo`
   - `diferencia_score = recaudable - score_tarjeta`
   - Si `|diferencia_score| > tolerancia_pesos` → se pide causa de irregularidad
   - `delta_entrada = contador_entrada_actual - contador_entrada_prev`
   - `delta_salida = contador_salida_actual - contador_salida_prev`
4. **Omitir máquina**: Si no se puede acceder, se registra con motivo de omisión.
5. **Cerrar corte** (cambia estado BORRADOR → CERRADO):
   - `total_recaudable = Σ recaudable` de todas las máquinas capturadas
   - `neto_cliente = total_recaudable * comision_pct`
   - `ganancia_dueno = total_recaudable - neto_cliente`
   - Estos valores se graban en el corte y ya no cambian.

### 4.2 Roles y Permisos

| Rol | Puede hacer |
|-----|------------|
| OPERADOR | Capturar máquinas, registrar gastos, ver dashboard propio |
| SUPERVISOR | Todo lo de operador + ver todas las rutas, cerrar cortes |
| ADMIN | Todo + CRUD usuarios, clientes, máquinas, rutas, catálogos, config |

### 4.3 Sincronización Offline-First (Flutter)

```
┌─────────────────────┐
│  App Flutter         │
│  ┌────────────────┐  │
│  │ SQLite local   │  │     ┌────────────────┐
│  │ (datos ref +   │◄─┼────►│ Backend FastAPI │
│  │  pendientes)   │  │     │ (tenant DB)    │
│  └────────────────┘  │     └────────────────┘
└─────────────────────┘
```

**Push**: Cortes, detalles, gastos creados offline se envían al server. El server responde con UUIDs definitivos y se remapean localmente.

**Pull**: Clientes, máquinas, rutas y catálogos se descargan del server y se insertan/actualizan en SQLite local.

### 4.4 Auto-Update de APK

1. Al iniciar la app, `UpdateService.checkForUpdate()` consulta `/zoreza-admin/api/releases/latest`
2. Compara `version_code` del server vs la local (`PackageInfo`)
3. Si hay update: muestra diálogo con release notes
4. Si `is_mandatory=true`: el diálogo no se puede cerrar
5. Descarga APK a directorio temporal, luego invoca instalación via `MethodChannel`

---

## 5. Flutter App — Estructura

### 5.1 Screens

| Screen | Archivo | Función |
|--------|---------|---------|
| Login | `screens/login/login_screen.dart` | Auth + pull reference data |
| Home | `screens/home/home_screen.dart` | Dashboard con resumen, botón sync |
| Lista de Cortes | `screens/corte/corte_list_screen.dart` | Crear corte, ver pendientes |
| Detalle Corte | `screens/corte/corte_detail_screen.dart` | Ver máquinas, imprimir ticket, cerrar |
| Captura | `screens/corte/capture_screen.dart` | Formulario de captura de máquina |
| Omitir | `screens/corte/omit_screen.dart` | Formulario de omisión |
| Gastos | `screens/gastos/gastos_screen.dart` | CRUD gastos |
| Admin | `screens/admin/admin_screen.dart` | Tabs: Usuarios, Clientes, Máquinas, Rutas |
| Historial | `screens/historial/historial_screen.dart` | Cortes cerrados con totales |

### 5.2 Providers (Riverpod)

| Provider | Tipo | Propósito |
|----------|------|-----------|
| `sharedPrefsProvider` | Provider\<SharedPreferences\> | Tokens y preferencias |
| `databaseProvider` | Provider\<AppDatabase\> | SQLite local |
| `apiClientProvider` | Provider\<ApiClient\> | HTTP client con JWT y auto-refresh |
| `authServiceProvider` | Provider\<AuthService\> | Login/logout |
| `syncServiceProvider` | Provider\<SyncService\> | Push/pull offline sync |
| `updateServiceProvider` | Provider\<UpdateService\> | Auto-update APK |
| `authStateProvider` | NotifierProvider | Estado: unknown/authenticated/unauthenticated |
| `currentUserProvider` | NotifierProvider | Datos del usuario logueado |

### 5.3 Servicios

- **ApiClient**: Cliente HTTP completo con todos los endpoints. Interceptor que refresca token en 401.
- **SyncService**: `fullSync()` → push pending → pull reference data. Remapeo de UUIDs locales a server.
- **UpdateService**: Check `/releases/latest`, download APK con progress callback, install via MethodChannel.
- **TicketPrinter**: Genera bytes ESC/POS para impresora térmica 58mm (bold, alignment, corte de papel).

---

## 6. Web Admin — Estructura

### 6.1 Páginas

| Ruta | Componente | Función |
|------|-----------|---------|
| `/` | Dashboard | Gráficas: recaudación, gastos, tendencias |
| `/clientes` | Clientes | CRUD clientes con comisión |
| `/maquinas` | Maquinas | CRUD máquinas, asignar a cliente |
| `/rutas` | Rutas | CRUD rutas, asignar/desasignar máquinas |
| `/cortes` | Cortes | Lista de cortes, filtros |
| `/cortes/:corteId` | CorteDetail | Detalle con máquinas, cerrar corte |
| `/gastos` | Gastos | CRUD gastos por categoría |
| `/usuarios` | Usuarios | CRUD usuarios con roles |
| `/reportes` | Reportes | Exportar datos a Excel |
| `/configuracion` | Configuracion | Logo, tolerancia, fondo sugerido |

### 6.2 API Client (`web/src/api.js`)

- `getTenantSlug()` → extrae slug de `window.location`
- Base URL: `/${slug}/api/v1`
- Token storage: `localStorage` (access_token, refresh_token)
- Auto-refresh: interceptor en `fetch` que detecta 401 y refresca automáticamente
- Todas las funciones retornan `Promise` y lanzan error si `!response.ok`

### 6.3 Super Admin Panel (`/zoreza-admin/`)

Acceso separado con su propia autenticación. Panel con tema oscuro y branding Zoreza Labs.

Funcionalidades:
- CRUD de tenants (crear, editar, activar/desactivar)
- Reset de contraseña del admin de cada tenant
- Gestión de releases APK (subir, ver, eliminar)
- Ver versión actual publicada

---

## 7. Deployment

### 7.1 Requisitos

- Python 3.11+ con `pip install -r requirements.txt`
- Node.js 20+ para el build del web (`cd web && npm install && npm run build`)
- Flutter 3.41+ para compilar la app Android
- `JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`
- `ANDROID_HOME=$HOME/android-sdk`

### 7.2 Ejecución

```bash
# Backend (sirve API + web estático)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Web (desarrollo)
cd web
npm run dev

# Flutter (build APK)
cd app
flutter build apk --release
```

### 7.3 Estructura de Archivos en Producción

```
data/
├── master.db                  ← BD maestra (tenants, superadmins, releases)
├── tenants/
│   ├── acme.db               ← BD del tenant "acme"
│   └── demo.db               ← BD del tenant "demo"
└── releases/
    └── zoreza-pro-1.2.0.apk  ← APKs subidos
```

### 7.4 Crear Nuevo Tenant

Al hacer POST `/zoreza-admin/api/tenants`:
1. Se crea registro en `master.db` tabla `tenants`
2. Se crea archivo `data/tenants/{slug}.db`
3. Se ejecutan migraciones del esquema tenant
4. Se crea usuario admin por defecto (username=slug, password temporal)

---

## 8. Convenciones de Código

- **Python**: async/await everywhere, SQLAlchemy 2.0 style (select(), scalar())
- **Flutter**: Riverpod para estado, Navigator.push() para navegación
- **React**: Hooks funcionales, useState + useEffect, fetch API nativo (no axios)
- **UUIDs**: Todos los modelos usan UUID4 como PK (no autoincrement)
- **Timezone**: Todo en `America/Mexico_City` (config.app_tz)
- **Naming**: snake_case en Python, camelCase en JS/Dart, UPPER_SNAKE para constantes
- **Auth**: Bearer token en header `Authorization`, refresh vía POST /auth/refresh

---

## 9. Credenciales por Defecto

- **Super Admin**: username=`zoreza`, password=`ZorezaLabs2026!`
- **Tenant Admin** (creado automáticamente): username=`{slug}`, password temporal configurable

---

## 10. Cosas Pendientes / Futuro

- Migración a PostgreSQL para producción de alto volumen
- Notificaciones push (Firebase Cloud Messaging)
- Reportes PDF generados en backend
- Integración con sistemas de pago
- Tests unitarios y de integración
- CI/CD pipeline (GitHub Actions)
