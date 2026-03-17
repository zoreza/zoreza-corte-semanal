# Sistema de Sincronización con Fallback Automático

## 📋 Descripción General

El sistema de sincronización implementa un mecanismo robusto de fallback automático entre Turso (SQLite en la nube) y SQLite local. Cuando Turso falla o no está disponible, el sistema automáticamente:

1. ✅ Cambia a SQLite local sin interrumpir la operación
2. 📝 Guarda todas las operaciones en una cola de sincronización
3. 🚨 Muestra un banner de alerta rojo en la UI
4. 🔄 Permite sincronización manual cuando Turso se recupere

## 🏗️ Arquitectura

### Componentes Principales

#### 1. `sync_service.py` - Servicio de Sincronización
- **Ubicación:** `zoreza/services/sync_service.py`
- **Funciones principales:**
  - `mark_turso_failed(error)` - Marca que Turso falló
  - `mark_turso_recovered()` - Marca que Turso se recuperó
  - `add_pending_operation(type, sql, params)` - Agrega operación a la cola
  - `sync_pending_operations()` - Sincroniza operaciones pendientes
  - `get_sync_state()` - Obtiene estado actual
  - `has_pending_operations()` - Verifica si hay operaciones pendientes

#### 2. `FallbackConnection` - Wrapper de Conexión
- **Ubicación:** `zoreza/db/core.py` (clase)
- **Características:**
  - Maneja conexión primaria (Turso) y fallback (SQLite local)
  - Detecta errores automáticamente
  - Cambia a fallback sin interrumpir operaciones
  - Guarda operaciones de escritura en cola

#### 3. Banner de Alerta en UI
- **Ubicación:** `zoreza/ui/app_shell.py`
- **Características:**
  - Banner rojo visible cuando hay fallback activo
  - Muestra número de operaciones pendientes
  - Botón "Intentar Sincronizar" (solo ADMIN)
  - Botón "Ver Detalles" con información completa

## 🔄 Flujo de Operación

### Escenario Normal (Turso Funcionando)
```
Usuario → Operación → Turso → ✅ Éxito
```

### Escenario con Fallo de Turso
```
Usuario → Operación → Turso ❌ Error
                    ↓
              SQLite Local ✅
                    ↓
         Cola de Sincronización 📝
                    ↓
            Banner de Alerta 🚨
```

### Sincronización Manual
```
Admin → Botón "Sincronizar" → Intenta Turso
                                    ↓
                              ✅ Éxito → Limpia cola
                                    ↓
                              ❌ Error → Mantiene cola
```

## 📁 Persistencia de Estado

El estado de sincronización se guarda en:
- **Archivo:** `data/sync_state.json`
- **Contenido:**
  ```json
  {
    "using_fallback": true/false,
    "pending_operations": [
      {
        "type": "execute",
        "sql": "INSERT INTO ...",
        "params": [...],
        "timestamp": "2024-01-01T12:00:00"
      }
    ],
    "last_error": "Error message",
    "last_error_time": "2024-01-01T12:00:00"
  }
  ```

## 🎯 Casos de Uso

### 1. Reboot de Streamlit Cloud
**Problema:** Al hacer reboot, los datos en SQLite local se pierden.

**Solución:**
- Las operaciones se guardan en `sync_state.json`
- Al reiniciar, el sistema carga el estado
- Si hay operaciones pendientes, muestra el banner
- Admin puede sincronizar manualmente

### 2. Fallo Temporal de Turso
**Problema:** Turso no responde por timeout o error de red.

**Solución:**
- Sistema detecta el error automáticamente
- Cambia a SQLite local sin interrumpir al usuario
- Guarda operaciones en cola
- Muestra banner de alerta

### 3. Recuperación de Turso
**Problema:** Turso vuelve a estar disponible.

**Solución:**
- Admin hace clic en "Intentar Sincronizar"
- Sistema ejecuta todas las operaciones pendientes en Turso
- Si tiene éxito, limpia la cola y quita el banner
- Si falla, mantiene la cola y el banner

## 🔧 Configuración

### Variables de Entorno
```bash
# Turso (requerido para sincronización)
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your-token

# SQLite local (fallback)
ZOREZA_DB_PATH=./data/zoreza.db
```

### Streamlit Secrets
```toml
# .streamlit/secrets.toml
TURSO_DATABASE_URL = "libsql://your-db.turso.io"
TURSO_AUTH_TOKEN = "your-token"
```

## 🚨 Alertas y Notificaciones

### Banner Rojo (Modo Fallback Activo)
- **Cuándo aparece:** Cuando Turso falla y hay operaciones pendientes
- **Información mostrada:**
  - Estado: "MODO FALLBACK ACTIVO"
  - Número de operaciones pendientes
  - Último error (opcional)
- **Acciones disponibles:**
  - "Intentar Sincronizar" (solo ADMIN)
  - "Ver Detalles" (muestra JSON completo)

### Sin Banner (Operación Normal)
- Turso funcionando correctamente
- No hay operaciones pendientes
- Sistema operando normalmente

## 📊 Monitoreo

### Para Administradores
1. **Verificar estado:**
   - Observar si aparece el banner rojo
   - Revisar número de operaciones pendientes

2. **Sincronizar manualmente:**
   - Hacer clic en "Intentar Sincronizar"
   - Esperar confirmación de éxito/error

3. **Ver detalles:**
   - Hacer clic en "Ver Detalles"
   - Revisar JSON con información completa

### Para Desarrolladores
```python
from zoreza.services import sync_service

# Obtener estado
state = sync_service.get_sync_state()
print(f"Fallback activo: {state['using_fallback']}")
print(f"Operaciones pendientes: {len(state['pending_operations'])}")

# Verificar si hay pendientes
if sync_service.has_pending_operations():
    count = sync_service.get_pending_count()
    print(f"Hay {count} operaciones pendientes")

# Sincronizar manualmente
success, message, synced = sync_service.sync_pending_operations()
if success:
    print(f"✅ {synced} operaciones sincronizadas")
else:
    print(f"❌ Error: {message}")
```

## 🔒 Seguridad

### Datos Sensibles
- Las operaciones en cola pueden contener datos sensibles
- El archivo `sync_state.json` debe estar en `.gitignore`
- No compartir logs que contengan el estado de sincronización

### Permisos
- Solo usuarios ADMIN pueden ver el botón de sincronización
- Todos los usuarios ven el banner de alerta
- El estado se guarda en el servidor, no en el cliente

## 🐛 Troubleshooting

### Problema: Banner no desaparece después de sincronizar
**Solución:**
1. Verificar que Turso esté realmente disponible
2. Revisar logs de error en la consola
3. Intentar sincronizar nuevamente
4. Si persiste, revisar `sync_state.json`

### Problema: Operaciones no se sincronizan
**Solución:**
1. Verificar credenciales de Turso
2. Probar conexión con `test_turso_connection()`
3. Revisar formato de operaciones en la cola
4. Verificar que no haya errores de SQL

### Problema: Datos se pierden después de reboot
**Solución:**
1. Verificar que `sync_state.json` exista
2. Confirmar que las operaciones estén en la cola
3. Sincronizar manualmente después del reboot
4. Si se perdieron, restaurar desde backup

## 📝 Notas Importantes

1. **Persistencia:** El archivo `sync_state.json` persiste entre reboots en Streamlit Cloud
2. **Orden:** Las operaciones se sincronizan en el orden en que fueron guardadas
3. **Atomicidad:** Cada operación se sincroniza individualmente
4. **Errores:** Si una operación falla, se mantiene en la cola
5. **Limpieza:** Solo se limpian operaciones que se sincronizaron exitosamente

## 🔄 Actualizaciones Futuras

### Posibles Mejoras
- [ ] Sincronización automática en segundo plano
- [ ] Reintentos automáticos con backoff exponencial
- [ ] Compresión de operaciones similares
- [ ] Dashboard de monitoreo de sincronización
- [ ] Alertas por email cuando hay muchas operaciones pendientes
- [ ] Exportación de operaciones pendientes para análisis

---

**Versión:** 1.0  
**Fecha:** 2024-01-01  
**Autor:** Bob (AI Assistant)