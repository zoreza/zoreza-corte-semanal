# Manual de la App Android — Zoreza Pro

## Índice

1. [Instalación](#1-instalación)
2. [Inicio de Sesión](#2-inicio-de-sesión)
3. [Pantalla Principal (Home)](#3-pantalla-principal-home)
4. [Realizar un Corte Semanal](#4-realizar-un-corte-semanal)
5. [Capturar una Máquina](#5-capturar-una-máquina)
6. [Omitir una Máquina](#6-omitir-una-máquina)
7. [Cerrar un Corte](#7-cerrar-un-corte)
8. [Imprimir Ticket Térmico](#8-imprimir-ticket-térmico)
9. [Registrar Gastos](#9-registrar-gastos)
10. [Sincronización](#10-sincronización)
11. [Actualizaciones Automáticas](#11-actualizaciones-automáticas)
12. [Panel de Administración](#12-panel-de-administración)
13. [Historial de Cortes](#13-historial-de-cortes)
14. [Solución de Problemas](#14-solución-de-problemas)

---

## 1. Instalación

### Desde APK Directo
1. Descarga el archivo APK desde el sitio de descargas proporcionado por tu administrador.
2. En tu dispositivo Android, ve a **Ajustes → Seguridad** y activa **Orígenes desconocidos** (o permite la instalación desde el navegador).
3. Abre el archivo APK descargado y sigue las instrucciones de instalación.
4. Una vez instalada, encontrarás la app **Zoreza Pro** en tu cajón de aplicaciones.

### Requisitos
- Android 6.0 (API 23) o superior
- Conexión a internet para la primera configuración
- Impresora térmica Bluetooth (opcional, para tickets)

---

## 2. Inicio de Sesión

1. Abre la app **Zoreza Pro**.
2. Ingresa tu **usuario** y **contraseña** proporcionados por tu administrador.
3. Presiona **Iniciar Sesión**.
4. La app descargará automáticamente los datos de referencia (clientes, máquinas, rutas, catálogos) para funcionamiento offline.

> **Nota**: Si no tienes conexión a internet, no podrás iniciar sesión por primera vez. Después del primer inicio, podrás usar la app sin conexión.

---

## 3. Pantalla Principal (Home)

Al iniciar sesión verás el **Dashboard** con:

- **Resumen del período**: Total recaudado, total gastos, neto.
- **Cortes pendientes**: Cortes en estado BORRADOR que requieren atención.
- **Botón de Sincronización** (ícono de flechas circulares): Envía datos pendientes al servidor y descarga actualizaciones.
- **Contador de pendientes**: Muestra cuántos registros están esperando ser sincronizados.

### Navegación
En la parte inferior encontrarás las pestañas principales:
- **Home** — Dashboard con resumen
- **Cortes** — Lista y creación de cortes
- **Gastos** — Registro de gastos
- **Admin** — Panel de administración (solo roles ADMIN)

---

## 4. Realizar un Corte Semanal

Un **corte semanal** registra la recaudación de todas las máquinas de un cliente durante una semana.

### Crear un Nuevo Corte
1. Ve a la pestaña **Cortes**.
2. Presiona el botón **+** o **Nuevo Corte**.
3. Selecciona el **cliente** de la lista.
4. Selecciona la **fecha del corte** (la app calculará automáticamente la semana correspondiente: lunes a domingo).
5. Presiona **Crear**.

El corte aparecerá en estado **BORRADOR** con todas las máquinas del cliente listas para captura.

---

## 5. Capturar una Máquina

1. Abre el corte en estado BORRADOR.
2. Selecciona una máquina de la lista (las máquinas sin capturar aparecen pendientes).
3. Llena los campos:

| Campo | Descripción |
|-------|------------|
| **Efectivo total** | Dinero encontrado dentro de la máquina |
| **Score tarjeta** | Lectura del score electrónico |
| **Fondo** | Dinero que se deja como fondo operativo |
| **Contador entrada** | Lectura actual del contador de entrada |
| **Contador salida** | Lectura actual del contador de salida |

4. La app calcula automáticamente:
   - **Recaudable** = Efectivo total − Fondo
   - **Diferencia** = Recaudable − Score tarjeta
   - **Delta contadores** = Actual − Anterior

5. Si la **diferencia** excede la tolerancia configurada, la app pedirá:
   - **Causa de irregularidad** (seleccionar del catálogo)
   - **Nota explicativa** (opcional)

6. Si hay un **evento de contador** (reset, cambio de máquina, etc.):
   - Selecciona el evento del catálogo
   - Agrega una nota si es necesario

7. Presiona **Guardar**.

---

## 6. Omitir una Máquina

Si no puedes acceder a una máquina durante el corte:

1. Desde el detalle del corte, selecciona la máquina.
2. Presiona **Omitir**.
3. Selecciona el **motivo de omisión** del catálogo (ej: local cerrado, máquina en reparación).
4. Agrega una nota opcional.
5. Presiona **Confirmar**.

La máquina aparecerá marcada como **OMITIDA** y no se incluirá en los cálculos del corte.

---

## 7. Cerrar un Corte

Cuando todas las máquinas estén capturadas u omitidas:

1. Abre el corte.
2. Verifica que todas las máquinas tengan estado (capturada u omitida).
3. Presiona **Cerrar Corte**.
4. La app calculará automáticamente:
   - **Total recaudable** = Suma de recaudable de todas las máquinas capturadas
   - **Neto cliente** = Total recaudable × comisión del cliente (ej: 40%)
   - **Ganancia dueño** = Total recaudable − Neto cliente

5. El corte cambiará a estado **CERRADO** y ya no se podrá modificar.

> **Importante**: Asegúrate de que todos los datos sean correctos antes de cerrar. Un corte cerrado no se puede reabrir.

---

## 8. Imprimir Ticket Térmico

### Requisitos
- Impresora térmica Bluetooth de 58mm
- Bluetooth activado en tu dispositivo
- Impresora emparejada previamente

### Imprimir
1. Desde el detalle de un **corte cerrado**, presiona **Imprimir Ticket**.
2. Selecciona tu impresora Bluetooth.
3. El ticket se imprimirá con:
   - Nombre del cliente
   - Período (semana)
   - Detalle por máquina (efectivo, tarjeta, fondo, neto)
   - Máquinas omitidas con motivo
   - Totales: neto cliente, ganancia dueño, gastos
   - Nombre del operador

---

## 9. Registrar Gastos

1. Ve a la pestaña **Gastos**.
2. Presiona **+** para agregar un gasto.
3. Llena los campos:
   - **Fecha**
   - **Categoría**: Refacciones, Fondos/Robos, Permisos, Empleados, Servicios, Transporte, Otro
   - **Descripción** (breve)
   - **Monto**
   - **Notas** (opcional)
4. Presiona **Guardar**.

Para eliminar un gasto, desliza hacia la izquierda sobre el registro.

---

## 10. Sincronización

La app funciona **offline-first**: puedes capturar datos sin conexión y sincronizar después.

### Sincronización Manual
1. Desde la pantalla **Home**, presiona el ícono de sincronización (flechas circulares).
2. La app:
   - **Envía** al servidor: cortes, detalles y gastos pendientes.
   - **Descarga** del servidor: clientes, máquinas, rutas y catálogos actualizados.
3. Un mensaje confirmará el resultado.

### Indicador de Pendientes
El badge numérico junto al botón de sync muestra cuántos registros están esperando sincronización. Sincroniza regularmente para evitar acumular datos no respaldados.

---

## 11. Actualizaciones Automáticas

La app verifica automáticamente si hay una nueva versión disponible al iniciar.

- **Actualización opcional**: Aparece un diálogo con las notas de la versión. Puedes actualizar ahora o después.
- **Actualización obligatoria**: El diálogo no se puede cerrar. Debes actualizar para continuar usando la app.

El proceso:
1. Se muestra la barra de progreso de descarga.
2. Al completar, se abre el instalador de Android.
3. Autoriza la instalación y espera a que termine.

---

## 12. Panel de Administración

> **Solo disponible para usuarios con rol ADMIN**

Desde la pestaña **Admin** puedes gestionar:

### Usuarios
- Ver lista de usuarios del sistema
- Crear nuevo usuario (nombre, username, contraseña, rol, teléfono, email)
- Editar usuario existente
- Activar/desactivar usuarios

### Clientes
- Ver lista de clientes (dueños de establecimientos)
- Crear/editar cliente (nombre, teléfono, email, dirección, comisión %)
- Activar/desactivar clientes

### Máquinas
- Ver lista de máquinas con código y fondo
- Crear/editar máquina (código, fondo, cliente asignado)
- Activar/desactivar máquinas

### Rutas
- Crear rutas para organizar visitas
- Asignar/desasignar máquinas a rutas

---

## 13. Historial de Cortes

1. Accede a la sección **Historial**.
2. Verás todos los cortes con estado **CERRADO**.
3. Cada registro muestra:
   - Cliente
   - Período (semana)
   - Total recaudado
   - Neto cliente
   - Ganancia dueño
4. Puedes tocar cualquier corte para ver el detalle completo por máquina.

---

## 14. Solución de Problemas

### "No se puede conectar al servidor"
- Verifica tu conexión a internet (WiFi o datos móviles).
- Si estás en campo sin cobertura, trabaja offline y sincroniza después.

### "Credenciales incorrectas"
- Verifica que el usuario y contraseña sean correctos (distingue mayúsculas).
- Contacta a tu administrador si olvidaste tu contraseña.

### "Error al sincronizar"
- Revisa tu conexión a internet.
- Si persiste, cierra y abre la app.
- Si el error incluye "conflicto", contacta a tu administrador.

### "No se puede imprimir"
- Verifica que el Bluetooth esté activado.
- Asegúrate de que la impresora esté encendida y emparejada.
- Intenta desemparejar y volver a emparejar la impresora.

### "La app pide actualización obligatoria"
- Necesitas conexión a internet para descargar la nueva versión.
- Si la descarga falla, verifica tu espacio de almacenamiento disponible.
