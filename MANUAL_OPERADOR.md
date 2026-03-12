# 📖 Manual del Operador - Zoreza · Corte Semanal

**Versión 1.0** | Guía completa para operadores

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Acceso al Sistema](#acceso-al-sistema)
3. [Pantalla Principal](#pantalla-principal)
4. [Realizar un Corte Semanal](#realizar-un-corte-semanal)
5. [Consultar Historial](#consultar-historial)
6. [Cerrar Sesión](#cerrar-sesión)
7. [Preguntas Frecuentes](#preguntas-frecuentes)
8. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Introducción

### ¿Qué es Zoreza · Corte Semanal?

Es un sistema que te ayuda a registrar los cortes semanales de las máquinas expendedoras. Con esta aplicación puedes:

- ✅ Registrar los contadores de cada máquina
- ✅ Capturar el dinero recolectado
- ✅ Generar tickets de corte automáticamente
- ✅ Consultar el historial de cortes anteriores

### ¿Qué necesito?

- 🌐 Conexión a internet
- 💻 Computadora, tablet o celular con navegador web
- 🔑 Tu usuario y contraseña de operador

---

## 🔐 Acceso al Sistema

### Paso 1: Abrir la Aplicación

1. Abre tu navegador web (Chrome, Firefox, Safari, etc.)
2. Ingresa la dirección que te proporcionó tu supervisor
   - Ejemplo: `https://zoreza-corte.streamlit.app/`

### Paso 2: Iniciar Sesión

```
┌─────────────────────────────────────┐
│   🧾 Zoreza · Corte Semanal        │
│                                     │
│   Login requerido                   │
│                                     │
│   Usuario:  [operador          ]   │
│   Contraseña: [••••••••••••••••]   │
│                                     │
│          [ Entrar ]                 │
└─────────────────────────────────────┘
```

1. Escribe tu **usuario** (ejemplo: `operador`)
2. Escribe tu **contraseña**
3. Haz clic en el botón **"Entrar"**

**⚠️ IMPORTANTE:** 
- Si olvidas tu contraseña, contacta a tu supervisor
- No compartas tu usuario y contraseña con nadie

---

## 🏠 Pantalla Principal

Después de iniciar sesión, verás la pantalla principal:

```
┌────────────────────────────────────────────────────────────┐
│ Zoreza                                                      │
│ Tu Nombre                                                   │
│ Rol: OPERADOR                                              │
│                                                             │
│ Navegación                                                  │
│ ┌─────────────────────────────────────┐                   │
│ │ 📊 Operación · Corte semanal       │ ← Seleccionado    │
│ └─────────────────────────────────────┘                   │
│ ┌─────────────────────────────────────┐                   │
│ │ 📜 Historial                        │                   │
│ └─────────────────────────────────────┘                   │
│                                                             │
│ ─────────────────────────────────────                      │
│                                                             │
│ 🚪 Cerrar sesión                                           │
└────────────────────────────────────────────────────────────┘
```

### Elementos de la Pantalla

1. **Barra Lateral (Izquierda)**
   - Tu nombre y rol
   - Botones de navegación
   - Botón de cerrar sesión (al final)

2. **Área Principal (Derecha)**
   - Aquí aparecerá el contenido según la opción seleccionada

---

## 📊 Realizar un Corte Semanal

### Paso 1: Seleccionar Cliente

```
┌─────────────────────────────────────────────────────────────┐
│ Operación · Corte semanal                                   │
│                                                              │
│ Cliente                                                      │
│ ┌──────────────────────────────────┐                       │
│ │ Alicia                      ▼    │ ← Selecciona cliente  │
│ └──────────────────────────────────┘                       │
│                                                              │
│ Fecha de corte                                              │
│ ┌──────────────────────────────────┐                       │
│ │ 2026/03/11                  📅   │ ← Fecha automática    │
│ └──────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

1. En el campo **"Cliente"**, haz clic en el menú desplegable
2. Selecciona el cliente del que vas a hacer el corte
3. La **"Fecha de corte"** se llena automáticamente con la fecha actual
   - Puedes cambiarla si es necesario haciendo clic en el calendario 📅

### Paso 2: Información de la Semana

Después de seleccionar el cliente, verás:

```
┌─────────────────────────────────────────────────────────────┐
│ Semana: 2026-03-09 — 2026-03-15                            │
│ (week_start=2026-03-09T00:00:00-06:00)                     │
│                                                              │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Corte en BORRADOR · id=8                               │ │
│ └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Información importante:**
- **Semana**: Muestra el período del corte (de lunes a domingo)
- **Estado**: BORRADOR significa que puedes editarlo
- **ID**: Número único del corte

### Paso 3: Capturar Máquinas

Ahora verás la sección de **Máquinas**:

```
┌─────────────────────────────────────────────────────────────┐
│ Máquinas                                                     │
│                                                              │
│ 📍 M-005 · Estado actual: OMITIDA                           │
│                                                              │
│ Acción                                                       │
│ ┌──────────────────────────────────┐                       │
│ │ CAPTURADA                   ▼    │ ← Selecciona acción   │
│ └──────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

#### Opciones de Acción

Para cada máquina, selecciona una de estas opciones:

1. **CAPTURADA** ✅
   - Usa esta opción cuando la máquina funcionó normalmente
   - Deberás ingresar contadores y dinero

2. **OMITIDA** ⏭️
   - Usa esta opción cuando NO pudiste revisar la máquina
   - Ejemplo: Local cerrado, no había acceso

3. **IRREGULARIDAD** ⚠️
   - Usa esta opción cuando hubo un problema
   - Ejemplo: Máquina descompuesta, dinero faltante

### Paso 4: Capturar Datos (Si seleccionaste CAPTURADA)

```
┌─────────────────────────────────────────────────────────────┐
│ Contador Inicial                                             │
│ ┌──────────────────────────────────┐                       │
│ │ 1000                              │ ← Contador anterior   │
│ └──────────────────────────────────┘                       │
│                                                              │
│ Contador Final                                               │
│ ┌──────────────────────────────────┐                       │
│ │ 1150                              │ ← Contador actual     │
│ └──────────────────────────────────┘                       │
│                                                              │
│ Monto Capturado ($)                                          │
│ ┌──────────────────────────────────┐                       │
│ │ 1500.00                           │ ← Dinero recolectado  │
│ └──────────────────────────────────┘                       │
│                                                              │
│ Notas (opcional)                                             │
│ ┌──────────────────────────────────┐                       │
│ │ Todo normal                       │                       │
│ └──────────────────────────────────┘                       │
│                                                              │
│          [ 💾 Guardar ]                                     │
└─────────────────────────────────────────────────────────────┘
```

**Instrucciones:**

1. **Contador Inicial**: Ya viene lleno con el último contador registrado
   - ⚠️ Verifica que coincida con el contador de la máquina

2. **Contador Final**: Ingresa el contador actual de la máquina
   - 📝 Anota el número exacto que muestra la máquina

3. **Monto Capturado**: Ingresa el dinero que recolectaste
   - 💵 Cuenta bien el dinero antes de ingresarlo
   - Usa punto para decimales (ejemplo: 1500.50)

4. **Notas**: (Opcional) Escribe cualquier observación
   - Ejemplo: "Máquina funcionando bien"
   - Ejemplo: "Faltaban $50 pesos"

5. Haz clic en **"💾 Guardar"**

### Paso 5: Capturar Más Máquinas

Si el cliente tiene más máquinas, repite el Paso 3 y 4 para cada una.

```
┌─────────────────────────────────────────────────────────────┐
│ 📍 M-006 · Estado actual: OMITIDA                           │
│ 📍 M-007 · Estado actual: OMITIDA                           │
│ 📍 M-008 · Estado actual: OMITIDA                           │
└─────────────────────────────────────────────────────────────┘
```

### Paso 6: Cerrar el Corte

Cuando hayas capturado todas las máquinas:

```
┌─────────────────────────────────────────────────────────────┐
│ Cerrar corte                                                 │
│                                                              │
│ ⚠️ Debe existir al menos 1 máquina CAPTURADA para cerrar.  │
│                                                              │
│          [ 🔒 Cerrar Corte ]                                │
└─────────────────────────────────────────────────────────────┘
```

1. Verifica que hayas capturado al menos una máquina
2. Haz clic en **"🔒 Cerrar Corte"**
3. Confirma la acción

**⚠️ IMPORTANTE:** 
- Una vez cerrado, NO podrás modificar el corte
- Solo los supervisores pueden editar cortes cerrados

### Paso 7: Imprimir Ticket

Después de cerrar el corte, verás el resumen:

```
┌─────────────────────────────────────────────────────────────┐
│ Resumen del Corte                                            │
│                                                              │
│ Total Capturado:     $1,500.00                              │
│ Comisión Casa (60%): $  900.00                              │
│ Pago Cliente (40%):  $  600.00                              │
│                                                              │
│          [ 🖨️ Imprimir Ticket ]                            │
└─────────────────────────────────────────────────────────────┘
```

1. Revisa que los montos sean correctos
2. Haz clic en **"🖨️ Imprimir Ticket"**
3. Se abrirá una ventana con el ticket
4. Usa la función de imprimir de tu navegador (Ctrl+P o Cmd+P)

**El ticket incluye:**
- Fecha y hora del corte
- Información del cliente
- Detalle de cada máquina
- Totales y comisiones
- Código QR (opcional)

---

## 📜 Consultar Historial

### Paso 1: Ir al Historial

1. En la barra lateral, haz clic en **"📜 Historial"**

```
┌─────────────────────────────────────────────────────────────┐
│ Historial de Cortes                                          │
│                                                              │
│ Filtros                                                      │
│ ┌──────────────┬──────────────┬──────────────┐            │
│ │ Cliente      │ Estado       │ Fecha        │            │
│ │ Todos    ▼   │ Todos    ▼   │ 📅 Rango    │            │
│ └──────────────┴──────────────┴──────────────┘            │
│                                                              │
│          [ 🔍 Buscar ]                                      │
└─────────────────────────────────────────────────────────────┘
```

### Paso 2: Filtrar Cortes

Puedes filtrar por:

1. **Cliente**: Selecciona un cliente específico o "Todos"
2. **Estado**: 
   - BORRADOR: Cortes sin cerrar
   - CERRADO: Cortes finalizados
   - Todos: Muestra ambos
3. **Fecha**: Selecciona un rango de fechas

### Paso 3: Ver Resultados

```
┌─────────────────────────────────────────────────────────────┐
│ Resultados (15 cortes encontrados)                           │
│                                                              │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Corte #8 - Alicia                                      │ │
│ │ Fecha: 2026-03-11 | Estado: CERRADO                   │ │
│ │ Total: $1,500.00 | Comisión: $900.00                  │ │
│ │                                                         │ │
│ │ [ Ver Detalle ]  [ 🖨️ Reimprimir ]                   │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Corte #7 - Alicia                                      │ │
│ │ Fecha: 2026-03-04 | Estado: CERRADO                   │ │
│ │ Total: $1,200.00 | Comisión: $720.00                  │ │
│ │                                                         │ │
│ │ [ Ver Detalle ]  [ 🖨️ Reimprimir ]                   │ │
│ └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Paso 4: Ver Detalle de un Corte

1. Haz clic en **"Ver Detalle"** del corte que quieras revisar
2. Verás toda la información:
   - Máquinas capturadas
   - Contadores
   - Montos
   - Notas

### Paso 5: Reimprimir Ticket

Si necesitas reimprimir un ticket:

1. Haz clic en **"🖨️ Reimprimir"**
2. Se abrirá el ticket en una nueva ventana
3. Imprime usando Ctrl+P o Cmd+P

---

## 🚪 Cerrar Sesión

**SIEMPRE cierra sesión cuando termines de trabajar**

### Pasos:

1. Desplázate hasta el final de la barra lateral
2. Haz clic en **"🚪 Cerrar sesión"**

```
┌────────────────────────────────────┐
│                                     │
│ ─────────────────────────────────  │
│                                     │
│ 🚪 Cerrar sesión                   │
└────────────────────────────────────┘
```

3. La sesión se cerrará automáticamente
4. Volverás a la pantalla de login

**⚠️ IMPORTANTE:** 
- Cierra sesión especialmente si usas una computadora compartida
- Esto protege tu cuenta y la información

---

## ❓ Preguntas Frecuentes

### ¿Qué hago si me equivoco al capturar una máquina?

**Si el corte está en BORRADOR:**
1. Puedes volver a capturar la máquina
2. Los datos nuevos reemplazarán los anteriores

**Si el corte ya está CERRADO:**
1. Contacta a tu supervisor
2. Solo ellos pueden editar cortes cerrados

### ¿Puedo hacer varios cortes el mismo día?

Sí, puedes hacer cortes de diferentes clientes el mismo día. Pero solo puedes hacer **UN corte por semana por cliente**.

### ¿Qué pasa si no puedo acceder a una máquina?

Selecciona la opción **"OMITIDA"** para esa máquina y agrega una nota explicando por qué (ejemplo: "Local cerrado").

### ¿Cómo sé si guardé correctamente?

Verás un mensaje verde que dice **"✅ Guardado exitosamente"** en la parte superior de la pantalla.

### ¿Puedo usar la app desde mi celular?

Sí, la aplicación funciona en cualquier dispositivo con navegador web (computadora, tablet, celular).

### ¿Qué hago si el contador inicial no coincide?

1. Verifica el contador en la máquina física
2. Si hay diferencia, anótalo en las notas
3. Contacta a tu supervisor para reportar la discrepancia

### ¿Puedo ver cortes de otros operadores?

Sí, en el historial puedes ver todos los cortes, sin importar quién los hizo.

---

## 🔧 Solución de Problemas

### No puedo iniciar sesión

**Posibles causas:**
- ❌ Usuario o contraseña incorrectos
- ❌ Tu cuenta está inactiva

**Solución:**
1. Verifica que escribiste bien tu usuario y contraseña
2. Contacta a tu supervisor si el problema persiste

### La página no carga

**Posibles causas:**
- ❌ No hay conexión a internet
- ❌ El servidor está en mantenimiento

**Solución:**
1. Verifica tu conexión a internet
2. Intenta recargar la página (F5 o Ctrl+R)
3. Espera unos minutos y vuelve a intentar
4. Contacta a tu supervisor si el problema continúa

### No aparecen las máquinas del cliente

**Posibles causas:**
- ❌ El cliente no tiene máquinas asignadas
- ❌ Las máquinas están inactivas

**Solución:**
1. Contacta a tu supervisor
2. Ellos pueden asignar máquinas al cliente

### El botón "Cerrar Corte" no funciona

**Posibles causas:**
- ❌ No has capturado ninguna máquina
- ❌ Todas las máquinas están OMITIDAS

**Solución:**
1. Debes capturar al menos UNA máquina
2. Verifica que ingresaste todos los datos requeridos

### Los números no se guardan correctamente

**Posibles causas:**
- ❌ Usaste coma (,) en lugar de punto (.)
- ❌ Ingresaste letras en campos numéricos

**Solución:**
1. Usa punto (.) para decimales: 1500.50 ✅
2. No uses comas: 1,500.50 ❌
3. Solo ingresa números en campos numéricos

### No puedo imprimir el ticket

**Posibles causas:**
- ❌ Bloqueador de ventanas emergentes activado
- ❌ Impresora no configurada

**Solución:**
1. Permite ventanas emergentes en tu navegador
2. Verifica que tu impresora esté conectada
3. Puedes guardar el ticket como PDF si no tienes impresora

---

## 📞 Contacto y Soporte

Si tienes problemas que no puedes resolver:

1. **Contacta a tu supervisor inmediatamente**
2. Explica claramente el problema
3. Si es posible, toma una captura de pantalla del error

**Información útil para reportar problemas:**
- ¿Qué estabas haciendo cuando ocurrió el error?
- ¿Qué mensaje de error apareció?
- ¿En qué dispositivo estás trabajando?

---

## ✅ Checklist del Operador

Antes de cerrar tu turno, verifica:

- [ ] Todos los cortes del día están cerrados
- [ ] Imprimiste todos los tickets necesarios
- [ ] No dejaste cortes en BORRADOR sin terminar
- [ ] Cerraste sesión correctamente

---

## 📝 Notas Importantes

1. **Siempre verifica los contadores** antes de guardar
2. **Cuenta bien el dinero** antes de ingresarlo
3. **Agrega notas** cuando algo sea inusual
4. **Cierra sesión** al terminar tu turno
5. **Reporta problemas** inmediatamente a tu supervisor

---

**¿Necesitas ayuda?** Contacta a tu supervisor

**Versión del manual:** 1.0  
**Última actualización:** Marzo 2026

---

**¡Gracias por usar Zoreza · Corte Semanal! 🎉**