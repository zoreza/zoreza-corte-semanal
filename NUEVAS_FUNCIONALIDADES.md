# 🚀 Nuevas Funcionalidades - Plan de Implementación

## 📋 Resumen de Cambios Solicitados

### 1. Campos Adicionales en Clientes
- ✅ Domicilio (opcional)
- ✅ Colonia (opcional)
- ✅ Teléfono (opcional)
- ✅ Población (opcional)

### 2. Campo en Máquinas
- ✅ Número de Permiso (rota cada 4-6 meses)

### 3. Rediseño de Asignaciones
- ✅ Cambiar de: Máquina → Ruta
- ✅ A: Cliente → Ruta (todas las máquinas del cliente)
- ✅ Permitir desasignar máquinas (pool de máquinas sin uso)

### 4. Sistema de Audit Log
- ✅ Registrar quién hace qué
- ✅ Capturar: creación de usuarios, máquinas, rutas, asignaciones
- ✅ Los cortes ya tienen el operador registrado

### 5. Control de Sesiones
- ✅ Un usuario no puede tener 2 sesiones simultáneas
- ✅ Forzar cierre de sesión anterior

### 6. Cambio de Contraseña para Operadores
- ✅ Operadores pueden cambiar su propia contraseña
- ✅ Sin necesidad de admin

### 7. Pestaña "Avanzado" en Admin
- ✅ Respaldo y descarga de BD
- ✅ Selector de BD múltiples (producción/pruebas)
- ✅ Banner rojo cuando está en modo pruebas

---

## 🗄️ Cambios en Base de Datos

### Modificaciones a Tablas Existentes

#### Tabla `clientes`
```sql
ALTER TABLE clientes ADD COLUMN domicilio TEXT;
ALTER TABLE clientes ADD COLUMN colonia TEXT;
ALTER TABLE clientes ADD COLUMN telefono TEXT;
ALTER TABLE clientes ADD COLUMN poblacion TEXT;
```

#### Tabla `maquinas`
```sql
ALTER TABLE maquinas ADD COLUMN numero_permiso TEXT;
ALTER TABLE maquinas ADD COLUMN fecha_permiso TEXT;
ALTER TABLE maquinas ADD COLUMN asignada INTEGER NOT NULL DEFAULT 1;
```

### Nuevas Tablas

#### Tabla `audit_log`
```sql
CREATE TABLE audit_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  usuario_id INTEGER NOT NULL,
  usuario_nombre TEXT NOT NULL,
  accion TEXT NOT NULL,
  entidad TEXT NOT NULL,
  entidad_id INTEGER,
  detalles TEXT,
  ip_address TEXT,
  FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);
```

#### Tabla `cliente_ruta` (nueva)
```sql
CREATE TABLE cliente_ruta(
  cliente_id INTEGER NOT NULL,
  ruta_id INTEGER NOT NULL,
  activo INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  created_by INTEGER NOT NULL,
  PRIMARY KEY (cliente_id, ruta_id),
  FOREIGN KEY(cliente_id) REFERENCES clientes(id),
  FOREIGN KEY(ruta_id) REFERENCES rutas(id)
);
```

#### Tabla `sesiones`
```sql
CREATE TABLE sesiones(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario_id INTEGER NOT NULL UNIQUE,
  session_token TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  last_activity TEXT NOT NULL,
  ip_address TEXT,
  FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);
```

#### Tabla `db_environments`
```sql
CREATE TABLE db_environments(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  db_path TEXT NOT NULL,
  es_produccion INTEGER NOT NULL DEFAULT 0,
  activo INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  created_by INTEGER NOT NULL
);
```

---

## 📝 Archivos a Modificar/Crear

### Base de Datos
- ✅ `zoreza/db/core.py` - Agregar nuevas tablas y campos
- ✅ `zoreza/db/repo.py` - Funciones CRUD para nuevas entidades
- ✅ `zoreza/db/migrations.py` - Script de migración para BD existentes

### Servicios
- ✅ `zoreza/services/audit_service.py` - Nuevo servicio de auditoría
- ✅ `zoreza/services/session_service.py` - Nuevo servicio de sesiones
- ✅ `zoreza/services/db_manager.py` - Nuevo gestor de BD múltiples

### UI
- ✅ `zoreza/ui/pages/admin.py` - Actualizar con nuevos campos y pestaña Avanzado
- ✅ `zoreza/ui/pages/perfil.py` - Nueva página para cambio de contraseña
- ✅ `zoreza/ui/pages/avanzado.py` - Nueva página de configuración avanzada
- ✅ `zoreza/ui/app_shell.py` - Agregar banner de modo pruebas y control de sesiones

---

## 🔄 Flujo de Implementación

### Fase 1: Base de Datos (Prioridad Alta)
1. Crear script de migración
2. Agregar nuevas tablas
3. Modificar tablas existentes
4. Actualizar funciones CRUD

### Fase 2: Servicios (Prioridad Alta)
1. Servicio de auditoría
2. Servicio de sesiones
3. Gestor de BD múltiples

### Fase 3: UI - Admin (Prioridad Media)
1. Actualizar formularios de clientes
2. Actualizar formularios de máquinas
3. Rediseñar asignaciones
4. Crear pestaña Avanzado

### Fase 4: UI - Usuario (Prioridad Media)
1. Página de perfil/cambio de contraseña
2. Banner de modo pruebas
3. Control de sesiones

### Fase 5: Testing (Prioridad Alta)
1. Probar migraciones
2. Probar nuevas funcionalidades
3. Verificar audit log
4. Verificar control de sesiones

---

## ⚠️ Consideraciones Importantes

### Migración de Datos
- Las BD existentes necesitan migración
- Crear script `migrations.py` que:
  - Detecte versión actual de BD
  - Aplique cambios incrementales
  - No pierda datos existentes

### Compatibilidad
- Mantener compatibilidad con código existente
- Campos nuevos son opcionales
- No romper funcionalidad actual

### Seguridad
- Audit log no debe ser editable por usuarios
- Sesiones deben expirar después de inactividad
- BD de pruebas claramente identificada

### Performance
- Índices en audit_log para búsquedas rápidas
- Limpieza periódica de sesiones expiradas
- Optimizar consultas de asignaciones

---

## 📊 Estimación de Tiempo

| Fase | Tiempo Estimado | Complejidad |
|------|----------------|-------------|
| Fase 1: Base de Datos | 2-3 horas | Alta |
| Fase 2: Servicios | 2-3 horas | Alta |
| Fase 3: UI Admin | 3-4 horas | Media |
| Fase 4: UI Usuario | 1-2 horas | Baja |
| Fase 5: Testing | 2-3 horas | Media |
| **TOTAL** | **10-15 horas** | **Alta** |

---

## 🎯 Orden de Implementación

Voy a implementar en este orden para minimizar errores:

1. ✅ Script de migración de BD
2. ✅ Nuevas tablas y campos
3. ✅ Servicio de auditoría
4. ✅ Actualizar repo.py con nuevas funciones
5. ✅ Servicio de sesiones
6. ✅ Gestor de BD múltiples
7. ✅ Actualizar UI de Admin
8. ✅ Crear página de perfil
9. ✅ Crear página Avanzado
10. ✅ Agregar banner y control de sesiones
11. ✅ Testing completo

---

## 📝 Notas de Implementación

### Audit Log
- Registrar: CREATE, UPDATE, DELETE, LOGIN, LOGOUT
- Formato: `{usuario} {acción} {entidad} #{id} - {detalles}`
- Ejemplo: `admin CREÓ usuario #5 - operador_juan`

### Sesiones
- Token único por usuario
- Expiración: 8 horas de inactividad
- Al login: cerrar sesión anterior automáticamente

### BD Múltiples
- Producción: `zoreza.db` (por defecto)
- Pruebas: `zoreza_test.db`
- Selector en UI para cambiar
- Variable de sesión para BD activa

### Asignaciones
- Cliente → Ruta (1 a muchos)
- Todas las máquinas del cliente heredan la ruta
- Máquinas sin asignar: `asignada = 0`

---

**Estado:** Planificación completa ✅  
**Próximo paso:** Comenzar implementación Fase 1