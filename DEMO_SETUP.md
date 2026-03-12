# 🎭 Configuración de Demo vs Producción

Esta guía explica cómo mantener dos versiones del proyecto: una para **producción** (tu negocio real) y otra para **demo** (que otros puedan probar).

---

## 📋 Estrategia Recomendada: Ramas de Git

### Concepto

```
main (producción)          demo (demostración)
    │                          │
    │                          │
    ├─ Datos reales           ├─ Datos de ejemplo
    ├─ Clientes reales        ├─ Clientes ficticios
    ├─ Usuarios reales        ├─ Usuarios demo
    └─ BD persistente         └─ BD se reinicia
```

---

## 🚀 Implementación Paso a Paso

### Paso 1: Crear Rama Demo

```bash
# Desde tu rama main
git checkout -b demo

# Ahora estás en la rama demo
```

### Paso 2: Modificar init_db.py para Demo

Vamos a crear datos de demostración más completos:

```python
# En zoreza/init_db.py
# Agregar al final del archivo una función para datos demo

def seed_demo_data():
    """Crea datos de demostración más completos"""
    from zoreza.db.repo import (
        create_usuario, create_cliente, create_maquina,
        create_ruta, set_usuario_ruta, set_maquina_ruta
    )
    from zoreza.services.passwords import hash_password
    
    print("🎭 Creando datos de DEMOSTRACIÓN...")
    
    # Usuarios demo
    admin_id = create_usuario("demo_admin", hash_password("demo123"), "Admin Demo", "ADMIN", 1, None)
    super_id = create_usuario("demo_supervisor", hash_password("demo123"), "Supervisor Demo", "SUPERVISOR", 1, admin_id)
    oper_id = create_usuario("demo_operador", hash_password("demo123"), "Operador Demo", "OPERADOR", 1, admin_id)
    
    # Clientes demo
    cliente1_id = create_cliente("Tienda La Esquina", 60.0, 1, admin_id)
    cliente2_id = create_cliente("Restaurante El Buen Sabor", 55.0, 1, admin_id)
    cliente3_id = create_cliente("Gimnasio FitLife", 65.0, 1, admin_id)
    
    # Máquinas demo
    create_maquina("DEMO-001", cliente1_id, 0, 1, admin_id)
    create_maquina("DEMO-002", cliente1_id, 0, 1, admin_id)
    create_maquina("DEMO-003", cliente2_id, 0, 1, admin_id)
    create_maquina("DEMO-004", cliente2_id, 0, 1, admin_id)
    create_maquina("DEMO-005", cliente3_id, 0, 1, admin_id)
    
    # Rutas demo
    ruta1_id = create_ruta("Ruta Centro", 1, admin_id)
    ruta2_id = create_ruta("Ruta Norte", 1, admin_id)
    
    print("✅ Datos de demostración creados")
    print("\n🔑 Credenciales DEMO:")
    print("   Admin:      demo_admin / demo123")
    print("   Supervisor: demo_supervisor / demo123")
    print("   Operador:   demo_operador / demo123")
```

### Paso 3: Crear Variable de Entorno para Demo

Modifica `zoreza/db/core.py`:

```python
import os

def init_db(seed=False):
    """Inicializa la base de datos"""
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    
    if seed:
        # Verificar si es modo demo
        is_demo = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        if is_demo:
            from zoreza.init_db import seed_demo_data
            seed_demo_data()
        else:
            from zoreza.init_db import seed_data
            seed_data()
```

### Paso 4: Configurar Streamlit para Demo

Crea `.streamlit/secrets.toml` en la rama demo:

```toml
# Solo para rama demo
DEMO_MODE = "true"
```

### Paso 5: Agregar Banner de Demo

Modifica `zoreza/ui/app_shell.py` para mostrar un banner en modo demo:

```python
import os

def run_app():
    init_db(seed=True)
    
    # Mostrar banner si es demo
    if os.getenv("DEMO_MODE", "false").lower() == "true":
        st.warning("🎭 **MODO DEMOSTRACIÓN** - Los datos se reinician periódicamente. Credenciales: demo_admin / demo123")
    
    # ... resto del código
```

### Paso 6: Commit y Push de Rama Demo

```bash
# Hacer commit de los cambios en rama demo
git add .
git commit -m "feat: Configurar modo demo con datos de ejemplo"

# Subir rama demo a GitHub
git push origin demo
```

### Paso 7: Deployar Ambas Versiones en Streamlit

#### Versión Producción (main)
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Deploy desde rama `main`
3. URL: `https://tu-usuario-zoreza-corte-semanal.streamlit.app`

#### Versión Demo (demo)
1. En Streamlit Cloud, crea una **nueva app**
2. Selecciona el mismo repositorio
3. **Branch: `demo`** ← Importante
4. Main file: `app.py`
5. En "Advanced settings" → "Secrets", agrega:
   ```toml
   DEMO_MODE = "true"
   ```
6. URL: `https://tu-usuario-zoreza-corte-semanal-demo.streamlit.app`

---

## 🔄 Mantener Ambas Versiones

### Actualizar Producción (main)

```bash
git checkout main
# Hacer cambios
git add .
git commit -m "feat: Nueva funcionalidad"
git push origin main
# Streamlit auto-deploya
```

### Actualizar Demo

```bash
# Opción 1: Merge desde main (recomendado)
git checkout demo
git merge main
git push origin demo

# Opción 2: Cherry-pick commits específicos
git checkout demo
git cherry-pick <commit-hash>
git push origin demo
```

---

## 🎨 Alternativa: Repositorios Separados

Si prefieres tener repositorios completamente separados:

### Paso 1: Crear Nuevo Repositorio

```bash
# Clonar tu repo actual
git clone https://github.com/tu-usuario/zoreza-corte-semanal.git zoreza-demo

cd zoreza-demo

# Cambiar el remote
git remote remove origin
git remote add origin https://github.com/tu-usuario/zoreza-corte-semanal-demo.git

# Hacer cambios para demo
# ... modificar init_db.py, agregar banner, etc.

# Push al nuevo repo
git push -u origin main
```

### Paso 2: Deploy Separado

Deploy cada repositorio en Streamlit Cloud como apps independientes.

**Ventajas:**
- ✅ Separación total
- ✅ Más fácil de entender
- ✅ No hay riesgo de mezclar código

**Desventajas:**
- ❌ Tienes que mantener dos repos
- ❌ Cambios deben aplicarse manualmente en ambos

---

## 🗄️ Alternativa: Base de Datos Separada

Otra opción es usar la misma app pero con diferentes bases de datos:

### Configuración

```python
# En zoreza/db/core.py
import os

def get_db_path():
    """Obtiene la ruta de la BD según el modo"""
    if os.getenv("DEMO_MODE", "false").lower() == "true":
        return "./data/zoreza_demo.db"
    else:
        return os.getenv("ZOREZA_DB_PATH", "./data/zoreza.db")

def connect():
    """Conecta a la base de datos"""
    db_path = get_db_path()
    # ... resto del código
```

### En Streamlit Cloud

**App Producción:**
- No configures DEMO_MODE
- Usa `zoreza.db`

**App Demo:**
- Configura `DEMO_MODE = "true"` en secrets
- Usa `zoreza_demo.db`

---

## 🔒 Seguridad y Mejores Prácticas

### Para Producción

1. **Credenciales Fuertes**
   ```bash
   # Cambia inmediatamente las credenciales por defecto
   admin / admin123 → admin / TuContraseñaSegura123!
   ```

2. **Secrets en Streamlit**
   ```toml
   # .streamlit/secrets.toml (NO subir a GitHub)
   ADMIN_PASSWORD = "tu-contraseña-segura"
   ```

3. **Backups Regulares**
   - Descarga la BD semanalmente
   - Guarda en lugar seguro

### Para Demo

1. **Banner Visible**
   ```python
   st.warning("🎭 MODO DEMO - Datos de ejemplo")
   ```

2. **Credenciales Públicas**
   ```
   demo_admin / demo123
   demo_operador / demo123
   ```

3. **Reinicio Periódico**
   - Considera reiniciar la BD demo cada semana
   - O agregar botón "Reiniciar Demo"

---

## 📊 Comparación de Opciones

| Característica | Ramas Git | Repos Separados | BD Separada |
|----------------|-----------|-----------------|-------------|
| Facilidad setup | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Mantenimiento | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Separación | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Costo | Gratis | Gratis | Gratis |
| Recomendado | ✅ | ⚠️ | ⚠️ |

---

## 🎯 Recomendación Final

**Usa la estrategia de Ramas Git** porque:

1. ✅ Mantienes un solo repositorio
2. ✅ Fácil de sincronizar cambios
3. ✅ Dos deployments independientes en Streamlit
4. ✅ Datos completamente separados
5. ✅ Fácil de mantener

**Flujo de trabajo:**
```
main (producción)
  ↓
  Hacer cambios
  ↓
  Commit & Push
  ↓
  Auto-deploy en Streamlit
  
demo (demostración)
  ↓
  Merge desde main
  ↓
  Commit & Push
  ↓
  Auto-deploy en Streamlit
```

---

## 🚀 Implementación Rápida

```bash
# 1. Crear rama demo
git checkout -b demo

# 2. Modificar para demo (ver Paso 2-5 arriba)
# ... hacer cambios ...

# 3. Commit
git add .
git commit -m "feat: Configurar modo demo"

# 4. Push
git push origin demo

# 5. Deploy en Streamlit Cloud
# - Nueva app desde rama 'demo'
# - Agregar DEMO_MODE=true en secrets
```

---

## 📞 Soporte

Si tienes dudas sobre la configuración:
1. Revisa los ejemplos de código arriba
2. Consulta la documentación de Streamlit Cloud
3. Prueba primero en local antes de deployar

---

**¡Listo para tener tu versión de producción y demo! 🎉**