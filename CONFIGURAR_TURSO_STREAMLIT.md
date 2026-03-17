# Configurar Turso en Streamlit Cloud

## Problema Actual

La aplicación está usando SQLite local en lugar de Turso, lo que causa que los datos se pierdan al reiniciar. Esto sucede porque **las credenciales de Turso no están configuradas en Streamlit Cloud**.

## Solución: Configurar Secrets en Streamlit Cloud

### Paso 1: Acceder a la configuración de Secrets

1. Ve a tu app en Streamlit Cloud: https://share.streamlit.io/
2. Haz clic en tu app "zoreza-corte-semanal"
3. Haz clic en el menú de 3 puntos (⋮) en la esquina superior derecha
4. Selecciona **"Settings"**
5. En el menú lateral, selecciona **"Secrets"**

### Paso 2: Agregar las credenciales de Turso

En el editor de secrets, pega exactamente esto:

```toml
TURSO_DATABASE_URL = "libsql://zoreza-corte-zoreza.aws-us-east-1.turso.io"
TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzM0NjI3MTYsImlkIjoiMDE5Y2U5YjEtMzEwMS03ZDk2LTkwMWYtZTY2Mzk2NTk1ZTZjIiwicmlkIjoiOTk2ODZhYjItMTc0ZS00OThkLTliNzEtMGU5NjY4ZTg4NDQ0In0.IwiFkSEa5_KI7zqTt2w2tf2itZF2d2WQScZDgDtj-E09M-TvO7mVIxTol-gutzeGVHBPshsRp6l2mymfCs5lCg"
```

### Paso 3: Guardar y reiniciar

1. Haz clic en **"Save"**
2. La app se reiniciará automáticamente
3. Espera 1-2 minutos a que se complete el reinicio

### Paso 4: Verificar que funciona

1. Abre la app
2. En la pantalla de login, deberías ver:
   - ✅ **"Turso configurado y funcionando"** (mensaje verde)
   - Si ves un mensaje de error, revisa el diagnóstico en el expander

3. Intenta entrar con:
   - Usuario: `admin`
   - Contraseña: `admin123`

## ¿Qué hace esto?

- **TURSO_DATABASE_URL**: La dirección de tu base de datos en Turso
- **TURSO_AUTH_TOKEN**: El token de autenticación para acceder a Turso

Con estas credenciales configuradas:
- ✅ Los datos se guardan en Turso (en la nube)
- ✅ Los datos persisten después de reiniciar
- ✅ No se pierde información

## Diagnóstico Automático

La app ahora incluye un diagnóstico automático que se muestra en la pantalla de login:

- ✅ Verde: Todo funciona correctamente
- ⚠️ Amarillo: Hay un problema de configuración
- ❌ Rojo: Error crítico

El diagnóstico te dirá exactamente qué falta o qué está mal configurado.

## Troubleshooting

### Si ves "TURSO_DATABASE_URL no encontrada"
- Verifica que copiaste exactamente el contenido del Paso 2
- Asegúrate de hacer clic en "Save"
- Espera a que la app se reinicie completamente

### Si ves "Turso configurado pero falla conexión"
- Verifica que el token no haya expirado
- Contacta al administrador de Turso

### Si ves "Usando SQLite local (fallback activo)"
- Esto significa que hubo un error previo y la app cayó en modo fallback
- Haz un "Reboot" completo de la app desde Streamlit Cloud
- Verifica que los secrets estén correctamente configurados

## Contacto

Si después de seguir estos pasos sigues teniendo problemas, contacta al equipo de desarrollo con:
- Screenshot de la pantalla de login
- Screenshot del diagnóstico (expander "🔍 Diagnóstico de conexión")