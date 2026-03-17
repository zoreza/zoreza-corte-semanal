# 🔧 Guía de Uso: Turso Admin Tool

## 📋 Descripción

`turso_admin.py` es una herramienta de línea de comandos para administrar directamente tu base de datos de Turso. Te permite:

- ✅ Ver todos los usuarios
- 🔐 Resetear contraseñas
- 👤 Crear usuarios
- 🔍 Ver detalles de usuarios
- 💻 Ejecutar queries SQL personalizadas

## 🚀 Cómo Usar

### Paso 1: Abrir Terminal

En tu computadora, abre una terminal en el directorio del proyecto:

```bash
cd /Users/mariolopez/Documents/zoreza/zoreza-corte-semanal
```

### Paso 2: Activar Entorno Virtual

```bash
source .venv/bin/activate
```

### Paso 3: Ejecutar el Script

```bash
python turso_admin.py
```

## 📖 Opciones del Menú

### Opción 1: Listar Todos los Usuarios

Muestra una tabla con todos los usuarios en la base de datos:

```
ID    Username        Nombre               Rol          Activo
------------------------------------------------------------
1     admin           Administrador        ADMIN        ✅ Sí
2     operador1       Juan Pérez           OPERADOR     ✅ Sí
```

**Usa esto para:**
- Ver qué usuarios existen
- Verificar si el usuario admin está en la BD
- Comprobar el estado de los usuarios

### Opción 2: Resetear Contraseña de Admin ⭐ (RECOMENDADO)

**Esta es la opción que necesitas ahora mismo.**

Resetea la contraseña del usuario `admin` a `admin123`.

```
✅ Contraseña de 'admin' reseteada a: admin123
🔐 Hash generado: pbkdf2_sha256$200000$...
✅ Verificación exitosa: La contraseña funciona correctamente
```

**Después de usar esta opción:**
1. Ve a tu app de Streamlit
2. Haz login con:
   - Username: `admin`
   - Password: `admin123`
3. Cambia la contraseña desde la app (Admin → Usuarios)

### Opción 3: Crear Usuario Admin

Crea un nuevo usuario admin si no existe.

**Usa esto si:**
- No hay ningún usuario admin en la BD
- Necesitas crear el usuario desde cero

### Opción 4: Ver Detalles de un Usuario

Muestra información completa de un usuario específico:

```
Ingresa el username: admin

DETALLES DEL USUARIO: admin
====================================
id             : 1
username       : admin
password_hash  : pbkdf2_sha256$200000$...
nombre         : Administrador
rol            : ADMIN
activo         : 1
created_at     : 2024-01-01T12:00:00
updated_at     : 2024-01-01T12:00:00
```

### Opción 5: Ejecutar Query SQL Personalizada

Permite ejecutar cualquier query SQL directamente en Turso.

**Ejemplos:**

```sql
-- Ver todos los usuarios
SELECT * FROM usuarios;

-- Ver solo admins
SELECT * FROM usuarios WHERE rol = 'ADMIN';

-- Actualizar nombre de usuario
UPDATE usuarios SET nombre = 'Nuevo Nombre' WHERE username = 'admin';

-- Ver todas las tablas
SELECT name FROM sqlite_master WHERE type='table';
```

### Opción 0: Salir

Cierra la herramienta.

## 🆘 Solución Rápida a tu Problema Actual

### Problema
No puedes entrar con ninguna contraseña (ni la nueva ni la vieja).

### Solución

1. **Abre terminal:**
   ```bash
   cd /Users/mariolopez/Documents/zoreza/zoreza-corte-semanal
   source .venv/bin/activate
   ```

2. **Ejecuta el script:**
   ```bash
   python turso_admin.py
   ```

3. **Selecciona opción 2:**
   ```
   Selecciona una opción: 2
   ```

4. **Confirma el reseteo:**
   ```
   ✅ Contraseña de 'admin' reseteada a: admin123
   ```

5. **Ve a tu app y entra con:**
   - Username: `admin`
   - Password: `admin123`

6. **Cambia la contraseña inmediatamente:**
   - Ve a Admin → Usuarios
   - Edita el usuario admin
   - Cambia la contraseña
   - **IMPORTANTE:** Espera a que aparezca el mensaje de éxito

## 🔍 Verificar Estado de la BD

Si quieres ver qué hay en tu BD actualmente:

```bash
python turso_admin.py
```

Luego selecciona opción 1 para ver todos los usuarios.

## ⚠️ Notas Importantes

### Sobre el Problema de Sincronización

El problema que experimentaste ocurrió porque:

1. Cambiaste la contraseña en la app
2. El cambio se guardó en SQLite local (no en Turso)
3. Hiciste reboot
4. SQLite local se borró
5. Turso nunca recibió el cambio

### Solución Permanente

Después de resetear la contraseña con este script:

1. **Siempre verifica el banner:** Si ves el banner rojo "MODO FALLBACK ACTIVO", NO cambies contraseñas
2. **Sincroniza primero:** Si hay banner, haz clic en "Intentar Sincronizar"
3. **Espera confirmación:** Asegúrate de que el banner desaparezca
4. **Entonces cambia:** Solo cambia contraseñas cuando NO haya banner

## 🛠️ Troubleshooting

### Error: "No se encontró configuración de Turso"

**Solución:**
Verifica que tengas configurado en `.streamlit/secrets.toml`:

```toml
TURSO_DATABASE_URL = "libsql://zoreza-corte-zoreza.aws-us-east-1.turso.io"
TURSO_AUTH_TOKEN = "tu-token-aqui"
```

### Error: "No se pudo conectar a Turso"

**Posibles causas:**
1. Token inválido o expirado
2. URL incorrecta
3. Sin conexión a internet

**Solución:**
Verifica tus credenciales en Turso Dashboard.

### Error: "Usuario 'admin' no encontrado"

**Solución:**
Usa la opción 3 para crear el usuario admin.

## 📞 Comandos Rápidos

```bash
# Resetear contraseña de admin (lo más común)
python turso_admin.py
# Luego selecciona: 2

# Ver usuarios
python turso_admin.py
# Luego selecciona: 1

# Crear admin si no existe
python turso_admin.py
# Luego selecciona: 3
```

## 🎯 Resumen

**Para resolver tu problema actual:**

```bash
cd /Users/mariolopez/Documents/zoreza/zoreza-corte-semanal
source .venv/bin/activate
python turso_admin.py
# Selecciona opción 2
# Entra a la app con admin/admin123
# Cambia la contraseña (sin banner rojo)
```

---

**¿Necesitas ayuda?** Ejecuta el script y prueba las opciones. Todas son seguras y reversibles.