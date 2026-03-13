# Migración a Versión 2.0

## 📋 Resumen de Cambios

Esta migración agrega las siguientes mejoras al sistema:

### 1. **Campos Opcionales en Clientes**
- Domicilio
- Colonia
- Teléfono
- Población

### 2. **Campos Adicionales en Máquinas**
- Número de Permiso (rota cada 4-6 meses)
- Fecha de Permiso
- Estado de Asignación (asignada/disponible)

### 3. **Nuevo Sistema de Asignaciones**
- **Antes:** Máquina → Ruta
- **Ahora:** Cliente → Ruta
- Todas las máquinas del cliente heredan automáticamente la ruta
- Permite desasignar máquinas (pool de máquinas disponibles)

### 4. **Compatibilidad**
- La tabla `maquina_ruta` se mantiene para compatibilidad
- Los datos existentes se migran automáticamente
- No se pierde información

---

## 🚀 Cómo Ejecutar la Migración

### Opción 1: Desde Python (Recomendado)

```bash
# Asegúrate de estar en el directorio del proyecto
cd /ruta/a/zoreza-corte-semanal

# Activa el entorno virtual
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows

# Ejecuta el script de migración
python -m zoreza.db.migration_v2
```

### Opción 2: Desde la Terminal

```bash
python zoreza/db/migration_v2.py
```

---

## ✅ Verificación Post-Migración

Después de ejecutar la migración, verifica que todo funcionó correctamente:

1. **Inicia la aplicación:**
   ```bash
   streamlit run app.py
   ```

2. **Verifica en Admin > Clientes:**
   - Los clientes existentes deben aparecer normalmente
   - Al editar un cliente, verás los nuevos campos opcionales

3. **Verifica en Admin > Máquinas:**
   - Las máquinas existentes deben aparecer normalmente
   - Al editar una máquina, verás los campos de permiso y asignación

4. **Verifica en Admin > Asignaciones:**
   - Verás "Cliente ↔ Ruta" en lugar de "Máquina ↔ Ruta"
   - Las asignaciones existentes deben haberse migrado automáticamente
   - Verás una sección "Pool de Máquinas Sin Asignar"

---

## 🔄 Rollback (Si algo sale mal)

Si necesitas revertir los cambios:

1. **Restaura el backup automático:**
   ```bash
   # Los backups se guardan en data/backups/
   cp data/backups/zoreza_backup_YYYYMMDD_HHMMSS.db data/zoreza.db
   ```

2. **O usa tu propio backup:**
   ```bash
   cp /ruta/a/tu/backup.db data/zoreza.db
   ```

---

## 📝 Notas Importantes

### Antes de Migrar

1. **Haz un backup manual de tu base de datos:**
   ```bash
   cp data/zoreza.db data/zoreza_backup_manual.db
   ```

2. **Verifica que no haya usuarios activos en el sistema**

3. **Asegúrate de tener permisos de escritura en el directorio `data/`**

### Durante la Migración

- La migración es **idempotente**: puedes ejecutarla múltiples veces sin problemas
- Si ya fue ejecutada, te mostrará un mensaje indicándolo
- El proceso toma menos de 1 segundo en bases de datos pequeñas

### Después de Migrar

1. **Asigna rutas a tus clientes:**
   - Ve a Admin > Asignaciones
   - Usa la sección "Cliente ↔ Ruta"
   - Todas las máquinas del cliente heredarán la ruta

2. **Actualiza información de permisos:**
   - Ve a Admin > Máquinas
   - Edita cada máquina para agregar número y fecha de permiso

3. **Gestiona máquinas sin asignar:**
   - Si tienes máquinas que no están en uso, desmarca "Asignada"
   - Aparecerán en el "Pool de Máquinas Sin Asignar"

---

## 🆘 Solución de Problemas

### Error: "Base de datos no encontrada"

**Causa:** La ruta de la base de datos no es correcta.

**Solución:**
```bash
# Verifica la variable de entorno
echo $ZOREZA_DB_PATH

# O usa la ruta por defecto
export ZOREZA_DB_PATH=./data/zoreza.db
```

### Error: "Permission denied"

**Causa:** No tienes permisos de escritura.

**Solución:**
```bash
# En Linux/Mac
chmod 755 data/
chmod 644 data/zoreza.db

# En Windows, verifica los permisos del archivo
```

### Error: "Database is locked"

**Causa:** La aplicación está corriendo.

**Solución:**
1. Cierra Streamlit (Ctrl+C)
2. Ejecuta la migración
3. Reinicia Streamlit

### La migración se ejecutó pero no veo los cambios

**Solución:**
1. Cierra completamente el navegador
2. Reinicia Streamlit
3. Abre la aplicación en una nueva ventana

---

## 📊 Detalles Técnicos

### Cambios en el Esquema

```sql
-- Clientes
ALTER TABLE clientes ADD COLUMN domicilio TEXT;
ALTER TABLE clientes ADD COLUMN colonia TEXT;
ALTER TABLE clientes ADD COLUMN telefono TEXT;
ALTER TABLE clientes ADD COLUMN poblacion TEXT;

-- Máquinas
ALTER TABLE maquinas ADD COLUMN numero_permiso TEXT;
ALTER TABLE maquinas ADD COLUMN fecha_permiso TEXT;
ALTER TABLE maquinas ADD COLUMN asignada INTEGER NOT NULL DEFAULT 1;

-- Nueva tabla
CREATE TABLE cliente_ruta(
  cliente_id INTEGER NOT NULL,
  ruta_id INTEGER NOT NULL,
  activo INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  created_by INTEGER,
  PRIMARY KEY (cliente_id, ruta_id),
  FOREIGN KEY(cliente_id) REFERENCES clientes(id),
  FOREIGN KEY(ruta_id) REFERENCES rutas(id)
);
```

### Migración de Datos

La migración automáticamente:
1. Agrupa las asignaciones de máquinas por cliente
2. Crea asignaciones Cliente→Ruta únicas
3. Mantiene las asignaciones Máquina→Ruta existentes
4. Marca todas las máquinas como "asignadas" por defecto

---

## 📞 Soporte

Si encuentras algún problema durante la migración:

1. Revisa los logs en la terminal
2. Verifica que el backup automático se haya creado
3. Consulta la sección de Solución de Problemas
4. Si el problema persiste, restaura el backup y contacta soporte

---

## ✨ Nuevas Funcionalidades Disponibles

Después de la migración, podrás:

1. **Gestionar información completa de clientes** con domicilio, colonia, teléfono y población
2. **Rastrear permisos de máquinas** con número y fecha de vencimiento
3. **Asignar rutas por cliente** en lugar de por máquina individual
4. **Mantener un pool de máquinas disponibles** para uso futuro
5. **Simplificar la gestión de rutas** al heredar automáticamente a todas las máquinas del cliente

---

**Versión:** 2.0  
**Fecha:** Marzo 2026  
**Compatibilidad:** Zoreza Corte Semanal v1.x