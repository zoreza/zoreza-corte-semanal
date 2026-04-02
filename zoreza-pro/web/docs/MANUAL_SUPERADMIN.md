# Manual del Panel de Super Administración — Zoreza Pro

## Índice

1. [Acceso al Panel](#1-acceso-al-panel)
2. [Dashboard de Super Admin](#2-dashboard-de-super-admin)
3. [Gestión de Tenants](#3-gestión-de-tenants)
4. [Reseteo de Contraseñas](#4-reseteo-de-contraseñas)
5. [Gestión de Releases APK](#5-gestión-de-releases-apk)
6. [Arquitectura Multi-Tenant](#6-arquitectura-multi-tenant)

---

## 1. Acceso al Panel

### URL de Acceso
```
https://tu-servidor.com/zoreza-admin/
```

### Credenciales
El acceso al panel de Super Admin es separado del sistema de tenants. Usa las credenciales de super administrador proporcionadas durante la instalación.

### Interfaz
El panel usa un tema oscuro con los colores de Zoreza Labs (fondo negro, acentos naranjas). El logo de Zoreza Labs aparece en la parte superior.

---

## 2. Dashboard de Super Admin

Al ingresar verás un resumen del sistema:
- **Número total de tenants** registrados
- **Tenants activos** vs inactivos
- **Última release APK** publicada con su versión

---

## 3. Gestión de Tenants

Un **tenant** es un negocio independiente que usa Zoreza Pro con su propia base de datos aislada.

### Ver Tenants
La tabla muestra todos los tenants con:
- **Slug** — Identificador URL del tenant (ej: "acme")
- **Nombre** — Nombre del negocio
- **Contacto** — Nombre, email y teléfono
- **Plan** — Plan contratado
- **Estado** — Activo/Inactivo

### Crear Nuevo Tenant

1. Click en **Nuevo Tenant**.
2. Llena los campos:

| Campo | Obligatorio | Descripción |
|-------|:-----------:|------------|
| Slug | ✅ | Identificador URL (solo letras minúsculas, números y guiones). Ej: "pizzas-mario" |
| Nombre | ✅ | Nombre del negocio visible |
| Contacto nombre | | Persona de contacto |
| Contacto email | | Email de contacto |
| Contacto teléfono | | Teléfono de contacto |
| Plan | | Plan contratado (default: "basico") |
| Notas | | Notas internas |

3. Click en **Crear**.

### ¿Qué sucede al crear un tenant?
1. Se registra el tenant en la base de datos maestra.
2. Se crea una **base de datos aislada** exclusiva para este tenant (`data/tenants/{slug}.db`).
3. Se ejecutan automáticamente las migraciones del esquema.
4. Se crea un **usuario administrador por defecto** con username igual al slug.

> **Importante**: Después de crear el tenant, usa la función de **Reset de Contraseña** para establecer la contraseña del admin.

### Editar Tenant
1. Click en el ícono de edición junto al tenant.
2. Modifica nombre, contacto, plan o notas.
3. Click en **Guardar**.

### Activar/Desactivar Tenant
- Un tenant **inactivo** no puede acceder al sistema (ni web ni app).
- Desactiva el switch de **Activo** para suspender temporalmente un tenant.
- Los datos del tenant se conservan y puede reactivarse en cualquier momento.

---

## 4. Reseteo de Contraseñas

Si un tenant olvida la contraseña de su usuario administrador:

1. En la tabla de tenants, click en el ícono de **llave** o **Reset Password**.
2. Ingresa la **nueva contraseña**.
3. Click en **Confirmar**.
4. Comunica la nueva contraseña al administrador del tenant por un canal seguro.

> **Nota**: Esto resetea la contraseña del usuario administrador principal del tenant (el que se creó automáticamente). Los demás usuarios del tenant deben ser gestionados desde dentro del sistema del tenant.

---

## 5. Gestión de Releases APK

El sistema permite distribuir actualizaciones de la app Android directamente, sin necesidad de Play Store.

### Ver Releases
La tabla muestra todas las releases con:
- **Versión** (nombre y código)
- **Tamaño** del archivo
- **Notas de versión**
- **Obligatoria** (sí/no)
- **Fecha de publicación**

### Subir Nueva Release

1. Click en **Nueva Release**.
2. Llena los campos:

| Campo | Obligatorio | Descripción |
|-------|:-----------:|------------|
| Archivo APK | ✅ | El archivo .apk compilado |
| Nombre de versión | ✅ | Versión legible (ej: "1.2.0") |
| Código de versión | ✅ | Número entero incremental (ej: 3). La app compara este número para detectar actualizaciones. |
| Notas de versión | | Descripción de cambios (se muestra al usuario en el diálogo de actualización) |
| Obligatoria | | Si está marcado, los usuarios NO podrán seguir usando la app sin actualizar |

3. Click en **Subir**.
4. Se mostrará una barra de progreso durante la carga del archivo.

### ¿Cómo funciona la auto-actualización?
1. Cuando la app Android inicia, consulta el endpoint `/zoreza-admin/api/releases/latest`.
2. Compara el `version_code` del servidor contra la versión instalada.
3. Si hay una versión más nueva:
   - **Release no obligatoria**: Muestra diálogo con opción de actualizar o ignorar.
   - **Release obligatoria**: El diálogo bloquea la app hasta que el usuario actualice.
4. La descarga se realiza directamente desde el servidor.

### Eliminar Release
Click en el ícono de eliminar junto a la release. Se pedirá confirmación.

> **Precaución**: Si eliminas la última release activa, las apps no encontrarán actualizaciones hasta que subas una nueva.

### Recomendaciones
- Siempre incrementa el `version_code` (nunca repitas un número).
- Usa `version_name` con formato semántico: `MAYOR.MENOR.PARCHE` (ej: 1.2.0).
- Marca como **obligatoria** solo cuando hay correcciones de seguridad críticas o cambios que rompen compatibilidad.
- Incluye notas de versión claras para que los usuarios sepan qué cambió.

---

## 6. Arquitectura Multi-Tenant

### Aislamiento de Datos
Cada tenant tiene su **propia base de datos SQLite** completamente separada. Esto significa:
- Un tenant **nunca** puede ver datos de otro tenant.
- Si un tenant tiene problemas en su base de datos, los demás no se ven afectados.
- Puedes respaldar o restaurar la base de datos de un tenant individualmente.

### Estructura de Archivos
```
data/
├── master.db                  ← Base de datos maestra (tenants, superadmins, releases)
├── tenants/
│   ├── acme.db               ← Base de datos del tenant "acme"
│   ├── demo.db               ← Base de datos del tenant "demo"
│   └── pizzas-mario.db       ← Base de datos del tenant "pizzas-mario"
└── releases/
    ├── zoreza-pro-1.0.0.apk  ← APKs almacenados
    └── zoreza-pro-1.1.0.apk
```

### URLs por Tenant
Cada tenant accede al sistema con su propio slug:
- **Web**: `https://servidor.com/{slug}/`
- **API**: `https://servidor.com/{slug}/api/v1/...`
- **App Android**: El slug se configura en la pantalla de login

### Planes
El campo "plan" es informativo por ahora. Puede usarse para implementar límites de uso en el futuro (número de máquinas, usuarios, etc.).
