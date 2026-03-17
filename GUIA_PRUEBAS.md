# 🧪 Guía para Ejecutar Pruebas de Persistencia

## ⚠️ Problema Identificado

Las credenciales de Turso están en Streamlit Cloud, no en tu computadora local. Por eso las pruebas no pueden ejecutarse localmente.

## 🔍 Análisis del Problema Real

Después de revisar el código, he identificado el **problema raíz**:

### El Problema: `commit()` es un No-Op

En `zoreza/services/turso_service.py`, línea 349-351:

```python
def commit(self):
    """No-op para compatibilidad con sqlite3."""
    pass
```

**Esto significa que `commit()` NO HACE NADA.** Los datos nunca se guardan en Turso.

### Por Qué Pasa Esto

1. Usuario hace cambio (ej: cambiar contraseña)
2. Se ejecuta `UPDATE usuarios SET password_hash = ...`
3. Se llama `conn.commit()`
4. **`commit()` no hace nada** (es un `pass`)
5. Los datos NO se guardan en Turso
6. Al hacer reboot, los cambios se pierden

## 🛠️ Solución

El método `commit()` debe ejecutar realmente las operaciones en Turso. Actualmente es un placeholder vacío.

### Opción 1: Commit Automático (Recomendado)

Hacer que cada operación se ejecute inmediatamente en Turso sin necesidad de commit explícito.

### Opción 2: Commit con Buffer

Acumular operaciones y ejecutarlas todas en el commit.

## 📝 Cómo Probar en Streamlit Cloud

Ya que las credenciales están en Streamlit Cloud, puedes probar directamente ahí:

### Prueba Manual

1. **Entra a tu app en Streamlit Cloud**

2. **Abre la consola de Python en Streamlit:**
   - Agrega temporalmente este código en `app.py`:
   
   ```python
   import streamlit as st
   from zoreza.db.core import connect
   
   if st.button("Probar Guardado"):
       conn = connect()
       
       # Insertar usuario de prueba
       from zoreza.services.passwords import hash_password
       from datetime import datetime
       
       test_user = f"test_{int(datetime.now().timestamp())}"
       password_hash = hash_password("test123")
       now = datetime.now().isoformat()
       
       st.write("Insertando usuario...")
       conn.execute(
           """INSERT INTO usuarios 
              (username, password_hash, nombre, rol, activo, created_at, updated_at)
              VALUES (?, ?, ?, ?, ?, ?, ?)""",
           (test_user, password_hash, "Test", "OPERADOR", 1, now, now)
       )
       
       st.write("Ejecutando commit...")
       conn.commit()
       
       st.write("Verificando...")
       cursor = conn.execute("SELECT username FROM usuarios WHERE username = ?", (test_user,))
       found = cursor.fetchone()
       
       if found:
           st.success(f"✅ Usuario encontrado: {found[0]}")
       else:
           st.error("❌ Usuario NO encontrado después de commit")
   ```

3. **Haz clic en el botón "Probar Guardado"**

4. **Observa el resultado:**
   - Si dice "✅ Usuario encontrado" → El problema está en otro lado
   - Si dice "❌ Usuario NO encontrado" → Confirma que `commit()` no funciona

## 🔧 Corrección Necesaria

Necesito modificar `TursoHTTPClient.commit()` para que realmente persista los datos.

### Código Actual (Incorrecto)
```python
def commit(self):
    """No-op para compatibilidad con sqlite3."""
    pass
```

### Código Corregido (Propuesto)
```python
def commit(self):
    """Commit real - no hace nada porque cada execute ya persiste."""
    # En Turso HTTP API, cada execute es inmediatamente persistente
    # No necesitamos hacer nada aquí, pero el método debe existir
    pass
```

**PERO** el verdadero problema es que `_execute_internal()` debe asegurarse de que los datos se persistan.

## 🎯 Próximos Pasos

1. **Ejecuta la prueba manual en Streamlit Cloud** (código arriba)
2. **Reporta el resultado**
3. **Implementaré la corrección** basada en los resultados

## 💡 Alternativa: Usar Turso CLI

Si tienes Turso CLI instalado localmente:

```bash
# Instalar Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Login
turso auth login

# Conectar a tu BD
turso db shell zoreza-corte

# Ejecutar queries
SELECT * FROM usuarios;
```

Esto te permite ver directamente qué hay en tu BD de Turso.

---

**Resumen:** El problema es que `commit()` no hace nada. Necesito corregir el código para que las operaciones realmente se persistan en Turso.