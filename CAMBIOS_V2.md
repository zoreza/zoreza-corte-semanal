# Cambios Implementados - Versión 2.0

## 📅 Fecha: Marzo 2026

---

## ✨ Nuevas Funcionalidades

### 1. Campos Opcionales en Clientes

**Ubicación:** Admin > Clientes

Se agregaron 4 campos opcionales para capturar información adicional de los clientes:

- **Domicilio** - Dirección completa del cliente
- **Colonia** - Colonia o barrio
- **Teléfono** - Número de contacto
- **Población** - Ciudad o municipio

**Características:**
- Todos los campos son opcionales (no obligatorios)
- Se muestran en formularios de creación y edición
- Organizados en 2 columnas para mejor visualización
- Los datos se guardan en la base de datos

---

### 2. Gestión de Permisos de Máquinas

**Ubicación:** Admin > Máquinas

Se agregaron campos para rastrear los permisos de operación de las máquinas:

- **Número de Permiso** - Identificador del permiso actual
- **Fecha de Permiso** - Fecha de emisión o vencimiento
- **Estado de Asignación** - Indica si la máquina está en uso o disponible

**Características:**
- Campos opcionales para flexibilidad
- Selector de fecha con calendario
- Checkbox "Asignada (en uso)" para control de estado
- Permite rastrear renovaciones (cada 4-6 meses típicamente)

---

### 3. Nuevo Sistema de Asignaciones: Cliente → Ruta

**Ubicación:** Admin > Asignaciones

**Cambio Principal:**
- **Antes:** Las asignaciones eran Máquina → Ruta (individual)
- **Ahora:** Las asignaciones son Cliente → Ruta (grupal)

**Ventajas:**
- Simplifica la gestión de rutas
- Todas las máquinas del cliente heredan automáticamente la ruta
- Reduce el trabajo administrativo
- Más lógico desde el punto de vista del negocio

**Interfaz:**
- Nueva sección "Cliente ↔ Ruta" en lugar de "Máquina ↔ Ruta"
- Mensaje informativo explicando el nuevo sistema
- Mantiene la sección "Usuario ↔ Ruta" sin cambios

---

### 4. Pool de Máquinas Sin Asignar

**Ubicación:** Admin > Asignaciones (parte inferior)

**Funcionalidad:**
- Permite desasignar máquinas que no están en uso
- Las máquinas desasignadas aparecen en un pool separado
- Útil para máquinas en mantenimiento, almacenadas o de respaldo
- Se pueden reasignar fácilmente cuando sea necesario

**Cómo usar:**
1. Ve a Admin > Máquinas
2. Edita la máquina que quieres desasignar
3. Desmarca el checkbox "Asignada (en uso)"
4. La máquina aparecerá en el pool de disponibles

---

## 🔧 Cambios Técnicos

### Base de Datos

**Tabla `clientes`:**
```sql
+ domicilio TEXT
+ colonia TEXT
+ telefono TEXT
+ poblacion TEXT
```

**Tabla `maquinas`:**
```sql
+ numero_permiso TEXT
+ fecha_permiso TEXT
+ asignada INTEGER NOT NULL DEFAULT 1
```

**Nueva tabla `cliente_ruta`:**
```sql
CREATE TABLE cliente_ruta(
  cliente_id INTEGER NOT NULL,
  ruta_id INTEGER NOT NULL,
  activo INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  created_by INTEGER,
  PRIMARY KEY (cliente_id, ruta_id),
  FOREIGN KEY(cliente_id) REFERENCES clientes(id),
  FOREIGN KEY(ruta_id) REFERENCES rutas(id)
)
```

**Índices nuevos:**
- `idx_maquinas_asignada` - Para filtrar máquinas por estado
- `idx_cliente_ruta` - Para optimizar consultas de asignaciones

---

### Archivos Modificados

1. **`zoreza/db/core.py`**
   - Actualizado esquema SQL con nuevos campos y tabla
   - Actualizado seed de datos para usar cliente_ruta

2. **`zoreza/db/repo.py`**
   - Actualizadas funciones `create_cliente()` y `update_cliente()` con nuevos parámetros
   - Actualizadas funciones `create_maquina()` y `update_maquina()` con nuevos parámetros
   - Agregadas funciones:
     - `list_cliente_ruta()` - Lista asignaciones Cliente→Ruta
     - `set_cliente_ruta()` - Crea/actualiza asignación Cliente→Ruta
     - `get_cliente_ruta()` - Obtiene ruta de un cliente
     - `list_maquinas_sin_asignar()` - Lista máquinas disponibles

3. **`zoreza/ui/pages/admin.py`**
   - Actualizado formulario de clientes con campos opcionales
   - Actualizado formulario de máquinas con campos de permiso y asignación
   - Rediseñada sección de Asignaciones:
     - Cambiado "Máquina ↔ Ruta" por "Cliente ↔ Ruta"
     - Agregada sección "Pool de Máquinas Sin Asignar"
     - Agregado mensaje informativo sobre el nuevo sistema

---

### Archivos Nuevos

1. **`zoreza/db/migration_v2.py`**
   - Script de migración automática
   - Agrega campos a tablas existentes
   - Crea nueva tabla cliente_ruta
   - Migra datos de maquina_ruta a cliente_ruta
   - Crea índices para optimización
   - Idempotente (se puede ejecutar múltiples veces)

2. **`MIGRACION_V2.md`**
   - Documentación completa del proceso de migración
   - Instrucciones paso a paso
   - Solución de problemas
   - Detalles técnicos

3. **`CAMBIOS_V2.md`** (este archivo)
   - Resumen de todas las funcionalidades nuevas
   - Documentación de cambios técnicos

---

## 🔄 Proceso de Migración

### Para Usuarios Existentes

1. **Hacer backup de la base de datos:**
   ```bash
   cp data/zoreza.db data/zoreza_backup.db
   ```

2. **Ejecutar migración:**
   ```bash
   python3 -m zoreza.db.migration_v2
   ```

3. **Verificar cambios:**
   - Iniciar la aplicación
   - Revisar Admin > Clientes (nuevos campos)
   - Revisar Admin > Máquinas (nuevos campos)
   - Revisar Admin > Asignaciones (nuevo sistema)

### Para Instalaciones Nuevas

No se requiere migración. El esquema actualizado se crea automáticamente al inicializar la base de datos.

---

## 📊 Impacto en Funcionalidad Existente

### ✅ Sin Cambios

- Sistema de cortes (operación normal)
- Historial de cortes
- Dashboard y métricas
- Sistema de gastos
- Gestión de usuarios
- Catálogos
- Configuración global
- Tickets térmicos
- Exportación CSV
- Sistema de backup

### 🔄 Compatibilidad

- La tabla `maquina_ruta` se mantiene para compatibilidad
- Los datos existentes se migran automáticamente
- No se pierde información durante la migración
- El sistema funciona con ambos métodos de asignación

---

## 🎯 Casos de Uso

### Caso 1: Agregar Información de Cliente

**Antes:**
- Solo se capturaba nombre y comisión

**Ahora:**
```
Nombre: Tienda El Sol
Comisión: 40%
Domicilio: Av. Principal 123
Colonia: Centro
Teléfono: 555-1234
Población: Guadalajara
```

### Caso 2: Rastrear Permisos de Máquinas

**Antes:**
- No había forma de rastrear permisos

**Ahora:**
```
Código: M-001
Cliente: Tienda El Sol
Número de Permiso: PERM-2026-001
Fecha de Permiso: 2026-03-01
Estado: Asignada ✓
```

### Caso 3: Asignar Ruta a Cliente

**Antes:**
- Asignar cada máquina individualmente a una ruta
- Si el cliente tiene 10 máquinas = 10 asignaciones

**Ahora:**
- Asignar el cliente a una ruta
- Todas las máquinas heredan automáticamente
- Si el cliente tiene 10 máquinas = 1 asignación

### Caso 4: Gestionar Máquinas de Respaldo

**Antes:**
- No había forma de marcar máquinas como no asignadas

**Ahora:**
- Desmarcar "Asignada (en uso)"
- La máquina aparece en el pool de disponibles
- Fácil de reasignar cuando se necesite

---

## 📈 Beneficios

1. **Mejor organización de datos**
   - Información completa de clientes
   - Rastreo de permisos de máquinas

2. **Simplificación administrativa**
   - Menos asignaciones que gestionar
   - Cambios de ruta más rápidos

3. **Mayor flexibilidad**
   - Pool de máquinas disponibles
   - Campos opcionales según necesidad

4. **Mejor trazabilidad**
   - Historial de permisos
   - Control de estado de máquinas

5. **Escalabilidad**
   - Fácil agregar más clientes
   - Fácil gestionar más máquinas

---

## 🔮 Próximas Funcionalidades (No Incluidas)

Las siguientes funcionalidades fueron planificadas pero no implementadas en esta versión:

1. **Sistema de Audit Log**
   - Registro de quién hace qué cambios
   - Historial de modificaciones

2. **Control de Sesiones Únicas**
   - Evitar múltiples sesiones simultáneas
   - Forzar cierre de sesión anterior

3. **Cambio de Contraseña por Usuario**
   - Operadores pueden cambiar su propia contraseña
   - Sin necesidad de admin

4. **Configuración Avanzada**
   - Pestaña "Avanzado" en Admin
   - Respaldo y descarga de BD
   - Selector de BD múltiples
   - Banner de modo pruebas

Estas funcionalidades se pueden implementar en una versión futura según prioridades.

---

## 📞 Soporte

Para preguntas o problemas:
1. Consulta `MIGRACION_V2.md` para detalles de migración
2. Revisa la sección de Solución de Problemas
3. Verifica que el backup esté disponible antes de migrar

---

**Versión:** 2.0  
**Compatibilidad:** Zoreza Corte Semanal v1.x  
**Fecha de Lanzamiento:** Marzo 2026