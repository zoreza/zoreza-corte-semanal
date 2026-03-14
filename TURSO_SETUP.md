# 🌐 Guía de Configuración de Turso

## ¿Qué es Turso?

**Turso** es SQLite en la nube, 100% gratis para uso personal y pequeños proyectos. Es perfecto para aplicaciones en Streamlit Cloud porque:

- ✅ **Persistencia de datos** - Tus datos no se pierden al reiniciar
- ✅ **100% Gratis** - Plan gratuito generoso (500 bases de datos)
- ✅ **Compatible con SQLite** - Usa el mismo SQL que ya conoces
- ✅ **Rápido** - Baja latencia desde cualquier parte del mundo
- ✅ **Fácil de usar** - Setup en menos de 5 minutos

---

## 📋 Requisitos Previos

- Una cuenta de GitHub (para Streamlit Cloud)
- Terminal/Consola (Mac, Linux, o Windows con WSL)
- 5 minutos de tu tiempo

---

## 🚀 Paso 1: Crear Cuenta en Turso

1. Ve a [turso.tech](https://turso.tech)
2. Click en "Sign Up" o "Get Started"
3. Inicia sesión con GitHub
4. Acepta los términos y condiciones

¡Listo! Ya tienes tu cuenta de Turso.

---

## 💻 Paso 2: Instalar Turso CLI

### En Mac/Linux:

```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

### En Windows (WSL):

```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

### Verificar instalación:

```bash
turso --version
```

Deberías ver algo como: `turso version v0.x.x`

---

## 🔐 Paso 3: Autenticarse

```bash
turso auth login
```

Esto abrirá tu navegador para autenticarte con GitHub. Autoriza la aplicación.

---

## 🗄️ Paso 4: Crear tu Base de Datos

```bash
turso db create zoreza-corte
```

**Salida esperada:**
```
Created database zoreza-corte in [region]
```

**Nota:** Puedes usar cualquier nombre, pero `zoreza-corte` es descriptivo.

---

## 🔗 Paso 5: Obtener la URL de Conexión

```bash
turso db show zoreza-corte --url
```

**Salida esperada:**
```
libsql://zoreza-corte-[tu-usuario].turso.io
```

**⚠️ IMPORTANTE:** Copia esta URL, la necesitarás en el Paso 7.

---

## 🎫 Paso 6: Crear Token de Autenticación

```bash
turso db tokens create zoreza-corte
```

**Salida esperada:**
```
eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MDk...
```

**⚠️ IMPORTANTE:** Copia este token completo, lo necesitarás en el Paso 7.

**Nota:** Este token es como una contraseña. No lo compartas públicamente.

---

## ⚙️ Paso 7: Configurar en la Aplicación

### Opción A: Desde la Interfaz Web (Recomendado)

1. Abre tu aplicación en Streamlit Cloud
2. Inicia sesión como **ADMIN**
3. Ve a **Admin > Base de Datos**
4. Pega la **URL** del Paso 5
5. Pega el **Token** del Paso 6
6. Click en **"🔍 Probar Conexión"**
7. Si todo está bien, click en **"💾 Guardar Configuración"**
8. Reinicia la aplicación

### Opción B: Usando Streamlit Secrets (Alternativa)

Si prefieres usar Streamlit Secrets:

1. Ve a https://share.streamlit.io/
2. Encuentra tu app
3. Click en "⋮" > "Settings" > "Secrets"
4. Agrega:

```toml
TURSO_DATABASE_URL = "libsql://zoreza-corte-[tu-usuario].turso.io"
TURSO_AUTH_TOKEN = "eyJhbGciOiJFZERTQS..."
```

5. Click en "Save"
6. Reinicia la app

---

## 📤 Paso 8: Migrar Datos Existentes (Opcional)

Si ya tienes datos en SQLite local:

1. Ve a **Admin > Base de Datos**
2. Sección **"📤 Migrar Datos a Turso"**
3. Click en **"🚀 Migrar Datos Locales a Turso"**
4. Espera a que termine la migración
5. Reinicia la aplicación

---

## ✅ Verificación

Para confirmar que todo funciona:

1. Ve a **Admin > Base de Datos**
2. Deberías ver: **"🌐 Usando Turso (Base de datos en la nube)"**
3. El tipo de BD debe mostrar: **"TURSO"**
4. Estado: **"✅ Configurado"**

---

## 🔧 Comandos Útiles de Turso CLI

### Listar tus bases de datos:
```bash
turso db list
```

### Ver información de una BD:
```bash
turso db show zoreza-corte
```

### Conectarse a la BD (shell interactivo):
```bash
turso db shell zoreza-corte
```

### Crear un backup:
```bash
turso db shell zoreza-corte .dump > backup.sql
```

### Restaurar desde backup:
```bash
turso db shell zoreza-corte < backup.sql
```

### Eliminar una BD:
```bash
turso db destroy zoreza-corte
```

---

## 🆘 Solución de Problemas

### Error: "command not found: turso"

**Causa:** Turso CLI no está instalado o no está en el PATH.

**Solución:**
```bash
# Reinstalar
curl -sSfL https://get.tur.so/install.sh | bash

# Agregar al PATH (si es necesario)
export PATH="$HOME/.turso:$PATH"
```

### Error: "authentication required"

**Causa:** No has iniciado sesión.

**Solución:**
```bash
turso auth login
```

### Error: "database already exists"

**Causa:** Ya existe una BD con ese nombre.

**Solución:**
```bash
# Usar otro nombre
turso db create zoreza-corte-2

# O eliminar la existente
turso db destroy zoreza-corte
turso db create zoreza-corte
```

### Error: "failed to connect" en la app

**Causa:** URL o Token incorrectos.

**Solución:**
1. Verifica que copiaste la URL completa
2. Verifica que copiaste el token completo
3. Genera un nuevo token:
   ```bash
   turso db tokens create zoreza-corte
   ```
4. Intenta de nuevo

### Error: "libsql-client not installed"

**Causa:** La librería de Python no está instalada.

**Solución:**
```bash
pip install libsql-client
```

---

## 💰 Límites del Plan Gratuito

Turso ofrece un plan gratuito muy generoso:

- ✅ **500 bases de datos**
- ✅ **9 GB de almacenamiento total**
- ✅ **1 billón de filas leídas/mes**
- ✅ **25 millones de filas escritas/mes**
- ✅ **Backups automáticos**

Para una aplicación de cortes semanales, esto es **más que suficiente**.

---

## 🔒 Seguridad

### Buenas Prácticas:

1. **No compartas tu token** - Es como una contraseña
2. **Usa Streamlit Secrets** - Para producción
3. **Rota tokens periódicamente** - Cada 3-6 meses
4. **Limita acceso** - Solo ADMIN puede configurar

### Rotar Token:

```bash
# Crear nuevo token
turso db tokens create zoreza-corte

# Actualizar en la app
# (ve a Admin > Base de Datos)

# Revocar token anterior (opcional)
turso db tokens revoke zoreza-corte [token-id]
```

---

## 📊 Monitoreo

### Ver uso de tu BD:

```bash
turso db show zoreza-corte
```

Esto muestra:
- Tamaño de la BD
- Número de conexiones
- Región
- Última actualización

### Dashboard Web:

1. Ve a [turso.tech/app](https://turso.tech/app)
2. Inicia sesión
3. Selecciona tu base de datos
4. Verás métricas en tiempo real

---

## 🚀 Próximos Pasos

Una vez configurado Turso:

1. ✅ Tus datos persisten entre reinicios
2. ✅ Puedes acceder desde cualquier lugar
3. ✅ Backups automáticos
4. ✅ Escalabilidad sin costo adicional

### Recomendaciones:

- Haz backups manuales periódicos (mensual)
- Monitorea el uso desde el dashboard
- Considera actualizar a plan pagado si creces mucho

---

## 📚 Recursos Adicionales

- **Documentación oficial:** [docs.turso.tech](https://docs.turso.tech)
- **Discord de Turso:** [discord.gg/turso](https://discord.gg/turso)
- **GitHub:** [github.com/tursodatabase](https://github.com/tursodatabase)
- **Blog:** [blog.turso.tech](https://blog.turso.tech)

---

## ❓ Preguntas Frecuentes

### ¿Puedo usar Turso gratis para siempre?

Sí, el plan gratuito no tiene límite de tiempo.

### ¿Qué pasa si excedo los límites?

Turso te notificará y podrás actualizar a un plan pagado.

### ¿Puedo tener múltiples bases de datos?

Sí, hasta 500 en el plan gratuito.

### ¿Es seguro?

Sí, Turso usa encriptación en tránsito y en reposo.

### ¿Puedo migrar de vuelta a SQLite local?

Sí, puedes exportar los datos en cualquier momento.

### ¿Funciona con Streamlit Community Cloud?

Sí, perfectamente. Es la combinación ideal.

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o contacta al equipo de Turso en Discord.

---

**Versión:** 1.0  
**Última actualización:** Marzo 2026  
**Compatibilidad:** Zoreza Corte Semanal v2.0+