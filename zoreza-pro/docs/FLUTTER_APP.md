# App Flutter Android — Zoreza Pro

Guía para implementar la aplicación móvil Android con soporte offline-first.

---

## ¿Por qué Flutter y no PWA?

| Necesidad del operador | PWA | Flutter |
|------------------------|-----|---------|
| Trabajar sin internet | ⚠️ Service Workers (limitado) | ✅ SQLite nativo |
| Imprimir ticket térmico 80mm | ❌ Web Bluetooth limitado | ✅ ESC/POS Bluetooth |
| Instalar sin Play Store | ✅ | ✅ APK directo |
| Rendimiento en campo | ⚠️ Depende del navegador | ✅ Compilado nativo |
| Acceso a cámara para fotos de máquinas | ⚠️ | ✅ Nativo |

---

## Arquitectura de la App

```
lib/
├── main.dart                    # Entry point
├── app.dart                     # MaterialApp + rutas
│
├── core/
│   ├── config.dart              # URLs, timeouts, constantes
│   ├── theme.dart               # Tema Material Design
│   └── di.dart                  # Inyección de dependencias (Riverpod)
│
├── data/
│   ├── local/
│   │   ├── database.dart        # SQLite (sqflite / drift)
│   │   ├── tables/              # Tablas locales (espejo del servidor)
│   │   │   ├── usuarios_table.dart
│   │   │   ├── clientes_table.dart
│   │   │   ├── maquinas_table.dart
│   │   │   ├── cortes_table.dart
│   │   │   ├── corte_detalle_table.dart
│   │   │   ├── gastos_table.dart
│   │   │   └── catalogs_table.dart
│   │   └── sync_queue.dart      # Cola de cambios pendientes
│   │
│   ├── remote/
│   │   ├── api_client.dart      # Dio HTTP client con interceptors
│   │   ├── auth_api.dart        # POST /auth/login, /refresh
│   │   ├── cortes_api.dart      # CRUD cortes
│   │   ├── admin_api.dart       # CRUD clientes, maquinas, rutas
│   │   └── sync_api.dart        # POST /sync/pull, /sync/push
│   │
│   └── repositories/
│       ├── auth_repository.dart
│       ├── corte_repository.dart    # Offline-first: local → remote
│       ├── cliente_repository.dart
│       └── sync_repository.dart     # Orquesta pull/push
│
├── domain/
│   ├── models/                  # Dart classes (from JSON / SQLite)
│   │   ├── usuario.dart
│   │   ├── cliente.dart
│   │   ├── maquina.dart
│   │   ├── corte.dart
│   │   ├── corte_detalle.dart
│   │   └── gasto.dart
│   │
│   └── services/
│       ├── calculations.dart    # recaudable, reparto, deltas
│       └── validations.dart     # Mismas reglas que el backend
│
├── presentation/
│   ├── auth/
│   │   └── login_screen.dart
│   │
│   ├── corte/
│   │   ├── corte_list_screen.dart
│   │   ├── corte_detail_screen.dart
│   │   ├── machine_capture_screen.dart
│   │   └── machine_omission_screen.dart
│   │
│   ├── historial/
│   │   └── historial_screen.dart
│   │
│   ├── admin/
│   │   ├── admin_screen.dart
│   │   ├── usuarios_tab.dart
│   │   ├── clientes_tab.dart
│   │   └── maquinas_tab.dart
│   │
│   ├── dashboard/
│   │   └── dashboard_screen.dart
│   │
│   ├── gastos/
│   │   └── gastos_screen.dart
│   │
│   ├── ticket/
│   │   ├── ticket_preview.dart
│   │   └── ticket_printer.dart  # ESC/POS Bluetooth
│   │
│   └── widgets/                 # Componentes reutilizables
│       ├── sync_indicator.dart  # Muestra estado de sincronización
│       ├── offline_banner.dart  # Banner "Sin conexión"
│       └── metric_card.dart
│
└── services/
    ├── connectivity_service.dart  # Detecta online/offline
    ├── sync_service.dart          # Background sync con WorkManager
    └── printer_service.dart       # Bluetooth thermal printing
```

---

## Dependencias clave (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State management
  flutter_riverpod: ^2.4.0
  
  # Networking
  dio: ^5.4.0
  
  # Local database
  sqflite: ^2.3.0
  # O alternativa más type-safe:
  # drift: ^2.16.0
  
  # Storage seguro para tokens
  flutter_secure_storage: ^9.0.0
  
  # Conectividad
  connectivity_plus: ^6.0.0
  
  # Background sync
  workmanager: ^0.5.2
  
  # Bluetooth printing
  esc_pos_bluetooth: ^0.4.1
  esc_pos_utils: ^1.1.0
  
  # UUID
  uuid: ^4.3.0
  
  # Dates
  intl: ^0.19.0
```

---

## Flujo Offline-First

```
┌──────────────────────────────────────────────────┐
│            FLUJO DE DATOS OFFLINE-FIRST           │
│                                                   │
│  1. Operador abre la app                          │
│     → Lee datos de SQLite local                   │
│     → Muestra UI inmediatamente                   │
│                                                   │
│  2. En background: checa conectividad             │
│     → Si ONLINE:                                  │
│       a. PULL: GET /sync/pull?since=last_version  │
│          → Actualiza SQLite local                 │
│       b. PUSH: POST /sync/push                    │
│          → Envía cambios marcados pending_sync    │
│          → Marca como synced en local             │
│                                                   │
│  3. Operador captura datos de máquina             │
│     → Guarda en SQLite local (sync_status=pending)│
│     → Si ONLINE: push inmediato en background     │
│     → Si OFFLINE: queda en cola local             │
│                                                   │
│  4. Cuando recupera internet                      │
│     → WorkManager dispara sync automático         │
│     → Resuelve conflictos (server wins para       │
│       cortes CERRADOS)                            │
│                                                   │
│  5. Impresión de ticket                           │
│     → Genera ESC/POS desde datos locales          │
│     → Conecta por Bluetooth a impresora 80mm      │
│     → No requiere internet                        │
└──────────────────────────────────────────────────┘
```

---

## SQLite Local — Schema

El schema local es un espejo simplificado del servidor:

```sql
-- Cada tabla tiene estas columnas de sync:
-- uuid TEXT PRIMARY KEY,
-- sync_status TEXT DEFAULT 'pending',  -- 'synced', 'pending', 'conflict'
-- sync_version INTEGER DEFAULT 0,
-- updated_at TEXT,
-- device_id TEXT

CREATE TABLE usuarios (
  uuid TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  nombre TEXT NOT NULL,
  rol TEXT NOT NULL,
  activo INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  sync_version INTEGER DEFAULT 0,
  updated_at TEXT
);

CREATE TABLE clientes (
  uuid TEXT PRIMARY KEY,
  nombre TEXT NOT NULL,
  comision_pct REAL DEFAULT 0.40,
  activo INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  sync_version INTEGER DEFAULT 0,
  updated_at TEXT
);

CREATE TABLE maquinas (
  uuid TEXT PRIMARY KEY,
  codigo TEXT UNIQUE NOT NULL,
  cliente_id TEXT NOT NULL REFERENCES clientes(uuid),
  activo INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  sync_version INTEGER DEFAULT 0,
  updated_at TEXT
);

CREATE TABLE cortes (
  uuid TEXT PRIMARY KEY,
  cliente_id TEXT NOT NULL REFERENCES clientes(uuid),
  week_start TEXT NOT NULL,
  week_end TEXT NOT NULL,
  fecha_corte TEXT,
  comision_pct_usada REAL,
  neto_cliente REAL DEFAULT 0,
  pago_cliente REAL DEFAULT 0,
  ganancia_dueno REAL DEFAULT 0,
  estado TEXT DEFAULT 'BORRADOR',
  created_by TEXT,
  sync_status TEXT DEFAULT 'pending',
  sync_version INTEGER DEFAULT 0,
  updated_at TEXT,
  device_id TEXT
);

CREATE TABLE corte_detalle (
  uuid TEXT PRIMARY KEY,
  corte_id TEXT NOT NULL REFERENCES cortes(uuid),
  maquina_id TEXT NOT NULL REFERENCES maquinas(uuid),
  estado_maquina TEXT DEFAULT 'CAPTURADA',
  -- ... all fields same as server ...
  sync_status TEXT DEFAULT 'pending',
  sync_version INTEGER DEFAULT 0,
  updated_at TEXT,
  device_id TEXT
);

-- Sync queue: tracks what needs to be pushed
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name TEXT NOT NULL,
  record_uuid TEXT NOT NULL,
  action TEXT NOT NULL,  -- 'upsert', 'delete'
  payload TEXT,          -- JSON snapshot
  created_at TEXT DEFAULT (datetime('now')),
  status TEXT DEFAULT 'pending'  -- 'pending', 'sent', 'failed'
);
```

---

## Impresión Térmica Bluetooth (ESC/POS)

```dart
// Ejemplo simplificado de impresión
import 'package:esc_pos_bluetooth/esc_pos_bluetooth.dart';
import 'package:esc_pos_utils/esc_pos_utils.dart';

Future<void> printTicket(Corte corte, List<CorteDetalle> detalles) async {
  final profile = await CapabilityProfile.load();
  final generator = Generator(PaperSize.mm80, profile);
  List<int> bytes = [];

  // Encabezado
  bytes += generator.text('ZOREZA',
    styles: PosStyles(align: PosAlign.center, bold: true, height: PosTextSize.size2));
  bytes += generator.text('CORTE SEMANAL',
    styles: PosStyles(align: PosAlign.center));
  bytes += generator.hr();

  // Info del corte
  bytes += generator.text('Cliente: ${corte.clienteNombre}');
  bytes += generator.text('Semana: ${corte.weekStart} - ${corte.weekEnd}');
  bytes += generator.hr();

  // Resumen
  bytes += generator.row([
    PosColumn(text: 'Total Recaudable:', width: 8),
    PosColumn(text: '\$${corte.netoCliente.toStringAsFixed(2)}', width: 4,
      styles: PosStyles(align: PosAlign.right)),
  ]);
  // ... más filas ...

  bytes += generator.cut();

  // Enviar por Bluetooth
  final printer = PrinterBluetooth(selectedDevice);
  await printerManager.printTicket(bytes);
}
```

---

## Comandos para crear el proyecto Flutter

```bash
# Crear proyecto
flutter create --org com.zoreza --project-name zoreza_pro zoreza_flutter
cd zoreza_flutter

# Agregar dependencias
flutter pub add flutter_riverpod dio sqflite flutter_secure_storage \
  connectivity_plus workmanager uuid intl esc_pos_bluetooth esc_pos_utils

# Generar APK
flutter build apk --release

# Instalar en dispositivo conectado
flutter install
```

---

## Próximos Pasos

1. **Backend** (este proyecto): ✅ Completo — levantar con Docker Compose
2. **App Flutter**: Crear proyecto con `flutter create`, implementar screens
3. **Sync Engine**: Implementar `/sync/pull` y `/sync/push` en el backend
4. **Testing**: Pruebas E2E con dispositivo real + impresora térmica
5. **Deploy**: Backend en Railway/Render/AWS + APK distribuido por WhatsApp/Drive
