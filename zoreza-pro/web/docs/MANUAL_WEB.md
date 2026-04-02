# Manual del Sitio Web de Administración — Zoreza Pro

## Índice

1. [Acceso al Sistema](#1-acceso-al-sistema)
2. [Dashboard](#2-dashboard)
3. [Gestión de Clientes](#3-gestión-de-clientes)
4. [Gestión de Máquinas](#4-gestión-de-máquinas)
5. [Gestión de Rutas](#5-gestión-de-rutas)
6. [Cortes Semanales](#6-cortes-semanales)
7. [Gestión de Gastos](#7-gestión-de-gastos)
8. [Gestión de Usuarios](#8-gestión-de-usuarios)
9. [Reportes y Exportaciones](#9-reportes-y-exportaciones)
10. [Configuración](#10-configuración)

---

## 1. Acceso al Sistema

### URL de Acceso
El sitio web se encuentra en la dirección de tu servidor, seguida del slug de tu tenant:

```
https://tu-servidor.com/{tu-slug}/
```

Por ejemplo: `https://zoreza.com/acme/`

### Inicio de Sesión
1. Ingresa tu **usuario** y **contraseña**.
2. Click en **Iniciar Sesión**.
3. El sistema te redirigirá al Dashboard.

> **Nota**: Las credenciales son las mismas que usas en la app Android. Tu administrador te proporcionó estas credenciales.

### Sesión y Seguridad
- La sesión dura **60 minutos** de inactividad. Después se refresca automáticamente.
- Si tu sesión expira completamente (30 días), deberás iniciar sesión nuevamente.
- Para cerrar sesión, click en **Cerrar Sesión** en la barra lateral.

---

## 2. Dashboard

El Dashboard muestra un resumen visual del negocio:

### Tarjetas de Resumen
- **Total Recaudado**: Suma de recaudable de todos los cortes en el período.
- **Total Gastos**: Suma de todos los gastos registrados.
- **Neto**: Diferencia entre recaudado y gastos.

### Gráficas
- **Tendencia de Recaudación**: Gráfica de líneas mostrando la recaudación semana a semana.
- **Gastos por Categoría**: Gráfica de barras desglosando gastos por tipo.

### Filtros
Puedes ajustar el período de visualización seleccionando fechas de inicio y fin.

---

## 3. Gestión de Clientes

> **Acceso**: Barra lateral → **Clientes**

Los **clientes** son los dueños de establecimientos donde están instaladas las máquinas.

### Ver Clientes
- Lista de todos los clientes con nombre, teléfono y porcentaje de comisión.
- Filtro para mostrar solo activos o incluir inactivos.

### Crear Cliente
1. Click en **Nuevo Cliente**.
2. Llena los campos:
   - **Nombre** (obligatorio)
   - **Teléfono**
   - **Email**
   - **Dirección postal**
   - **Comisión %** — Porcentaje que recibe el cliente por la recaudación de sus máquinas (default: 40%)
3. Click en **Guardar**.

### Editar Cliente
1. Click en el ícono de edición (lápiz) junto al cliente.
2. Modifica los campos necesarios.
3. Click en **Guardar**.

### Activar/Desactivar
Para desactivar un cliente sin eliminarlo, cambia el switch de **Activo** en la edición.

> **Nota sobre Comisión**: La comisión del cliente se aplica al cerrar un corte. Si cambias la comisión, solo afecta a cortes futuros.

---

## 4. Gestión de Máquinas

> **Acceso**: Barra lateral → **Máquinas**

### Ver Máquinas
- Lista con código de máquina, fondo asignado y cliente actual.
- Filtro por cliente y por estado (activas/inactivas).

### Crear Máquina
1. Click en **Nueva Máquina**.
2. Llena los campos:
   - **Código** (obligatorio, único) — Identificador de la máquina (ej: "M-001")
   - **Fondo** — Monto en efectivo que se deja en la máquina como fondo operativo (default: $0)
   - **Cliente** — Asignar a un cliente existente (opcional)
3. Click en **Guardar**.

### Editar Máquina
Modifica código, fondo o cliente asignado. Puedes reasignar una máquina a otro cliente.

---

## 5. Gestión de Rutas

> **Acceso**: Barra lateral → **Rutas**

Las **rutas** agrupan máquinas para organizar las visitas de los operadores.

### Crear Ruta
1. Click en **Nueva Ruta**.
2. Ingresa **Nombre** y **Descripción** (opcional).
3. Click en **Guardar**.

### Asignar Máquinas
1. Abre una ruta existente.
2. Verás las máquinas actualmente asignadas.
3. Click en **Agregar Máquina** para asignar nuevas máquinas.
4. Para desasignar, click en el ícono de eliminar junto a la máquina.

> **Nota**: Una máquina puede estar asignada a múltiples rutas.

---

## 6. Cortes Semanales

> **Acceso**: Barra lateral → **Cortes**

### Ver Cortes
- Lista de todos los cortes con cliente, período, estado y totales.
- Filtros por cliente, estado (BORRADOR/CERRADO) y fecha.

### Ver Detalle de un Corte
1. Click sobre un corte para ver su detalle.
2. Verás cada máquina con sus valores:
   - Efectivo, Score tarjeta, Fondo, Recaudable
   - Diferencia con score
   - Estado (capturada/omitida)
   - Notas de irregularidad o eventos

### Cerrar un Corte
1. Desde el detalle del corte (debe estar en BORRADOR).
2. Verifica que todas las máquinas estén procesadas.
3. Click en **Cerrar Corte**.
4. El sistema calculará los totales finales automáticamente.

> **Importante**: Un corte cerrado no se puede modificar. Verifica los datos antes de cerrar.

---

## 7. Gestión de Gastos

> **Acceso**: Barra lateral → **Gastos**

### Ver Gastos
- Lista de gastos con fecha, categoría, descripción y monto.
- Filtros por rango de fechas y categoría.

### Categorías Disponibles
| Categoría | Uso |
|-----------|-----|
| Refacciones | Piezas de repuesto para máquinas |
| Fondos/Robos | Reposición de fondos o pérdidas por robo |
| Permisos | Licencias y permisos gubernamentales |
| Empleados | Nómina y pagos a empleados |
| Servicios | Servicios públicos, internet, etc. |
| Transporte | Gasolina, peajes, mantenimiento vehicular |
| Otro | Gastos que no encajan en otras categorías |

### Crear Gasto
1. Click en **Nuevo Gasto**.
2. Selecciona **fecha**, **categoría**, ingresa **descripción**, **monto** y **notas** (opcional).
3. Click en **Guardar**.

### Eliminar Gasto
Click en el ícono de eliminar (basura) junto al gasto. Se pedirá confirmación.

---

## 8. Gestión de Usuarios

> **Acceso**: Barra lateral → **Usuarios** (solo ADMIN)

### Roles del Sistema

| Rol | Permisos |
|-----|---------|
| **OPERADOR** | Capturar máquinas, registrar gastos, ver su dashboard |
| **SUPERVISOR** | Todo lo de operador + ver todas las rutas, cerrar cortes |
| **ADMIN** | Acceso completo: CRUD de usuarios, clientes, máquinas, rutas, catálogos y configuración |

### Crear Usuario
1. Click en **Nuevo Usuario**.
2. Llena: **Nombre**, **Username**, **Contraseña**, **Rol**, **Teléfono**, **Email**.
3. Click en **Guardar**.

### Editar/Desactivar Usuario
- Edita nombre, teléfono, email, rol.
- Desactiva el switch **Activo** para bloquear el acceso sin eliminar el usuario.

---

## 9. Reportes y Exportaciones

> **Acceso**: Barra lateral → **Reportes**

### Exportar a Excel
1. Selecciona el tipo de datos a exportar.
2. Configura el rango de fechas si aplica.
3. Click en **Exportar**.
4. Se descargará un archivo `.xlsx` con los datos.

---

## 10. Configuración

> **Acceso**: Barra lateral → **Configuración** (solo ADMIN)

### Opciones Configurables

| Configuración | Descripción | Default |
|--------------|-------------|---------|
| **Tolerancia en pesos** | Diferencia máxima aceptable entre recaudable y score antes de pedir explicación | $30.00 |
| **Fondo sugerido** | Monto de fondo sugerido al crear una máquina | $500.00 |
| **Comisión por defecto** | Porcentaje de comisión para nuevos clientes | 40% |

### Logo del Tenant
1. Click en **Cambiar Logo**.
2. Selecciona una imagen (PNG o JPG, máximo 2MB).
3. El logo aparecerá en tickets y reportes.
