# 👨‍💼 Manual del Administrador - Zoreza · Corte Semanal

**Versión 1.0** | Guía completa para administradores

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Dashboard Principal](#dashboard-principal)
3. [Gestión de Gastos](#gestión-de-gastos)
4. [Gestión de Usuarios](#gestión-de-usuarios)
5. [Gestión de Clientes](#gestión-de-clientes)
6. [Gestión de Máquinas](#gestión-de-máquinas)
7. [Configuración de Rutas](#configuración-de-rutas)
8. [Catálogos del Sistema](#catálogos-del-sistema)
9. [Exportación de Datos](#exportación-de-datos)
10. [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Introducción

Como **Administrador**, tienes acceso completo al sistema. Tus responsabilidades incluyen:

- ✅ Monitorear el rendimiento del negocio
- ✅ Gestionar gastos operativos
- ✅ Administrar usuarios, clientes y máquinas
- ✅ Configurar catálogos y rutas
- ✅ Exportar datos para análisis
- ✅ Supervisar operaciones de corte

---

## 🏠 Dashboard Principal

### Acceso

1. Inicia sesión con tu cuenta de administrador
2. Verás automáticamente el **Dashboard** como página inicial

### Secciones del Dashboard

#### 📊 Resumen del Mes Actual

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Ingresos Totales    🏦 Comisión Casa                     │
│ $45,000.00             $27,000.00                           │
│ 12 cortes              60.0%                                │
│                                                              │
│ 💸 Gastos              📈 Ganancia Neta                     │
│ $8,500.00              $18,500.00                           │
│ 15 registros           Positivo                             │
└─────────────────────────────────────────────────────────────┘
```

**Métricas clave:**
- **Ingresos Totales**: Suma de todo el dinero capturado
- **Comisión Casa**: Tu porcentaje de ganancia (configurable por cliente)
- **Gastos**: Total de gastos registrados en el mes
- **Ganancia Neta**: Comisión menos gastos

#### 📉 Comparación Mensual

Gráfica de barras que compara:
- Mes anterior vs Mes actual
- Ingresos, Comisión, Gastos, Ganancia Neta

**Indicadores de cambio:**
- 🟢 Verde: Mejora respecto al mes anterior
- 🔴 Rojo: Disminución respecto al mes anterior

#### 💸 Distribución de Gastos

Gráfica circular que muestra gastos por categoría:
- 🔧 Refacciones
- 🚨 Fondos (Robos)
- 📋 Permisos
- 👥 Empleados
- ⚙️ Servicios
- 🚗 Transporte
- 📦 Otro

#### ⚡ Accesos Rápidos

Botones para acciones comunes:
- **📊 Nuevo Corte**: Ir a operación de corte
- **💰 Registrar Gasto**: Ir a módulo de gastos
- **📜 Ver Historial**: Consultar cortes anteriores
- **⚙️ Administración**: Ir a configuración

---

## 💰 Gestión de Gastos

### Acceso

Navegación → **💰 Gastos**

### Tab 1: Nuevo Gasto

#### Registrar un Gasto

```
┌─────────────────────────────────────────────────────────────┐
│ Fecha del gasto: [2026-03-12]  📅                          │
│                                                              │
│ Categoría: [REFACCIONES ▼]                                 │
│                                                              │
│ Monto ($): [1500.00]                                        │
│                                                              │
│ Descripción: [Reparación de máquina M-005]                 │
│                                                              │
│ Notas adicionales (opcional):                               │
│ [Cambio de pantalla y teclado]                             │
│                                                              │
│          [ 💾 Guardar Gasto ]                              │
└─────────────────────────────────────────────────────────────┘
```

**Categorías disponibles:**

1. **🔧 REFACCIONES**
   - Reparaciones de máquinas
   - Repuestos y componentes
   - Mantenimiento preventivo

2. **🚨 FONDOS_ROBOS**
   - Dinero faltante por robo
   - Pérdidas por vandalismo
   - Fondos de emergencia

3. **📋 PERMISOS**
   - Licencias de operación
   - Permisos municipales
   - Renovaciones anuales

4. **👥 EMPLEADOS**
   - Salarios
   - Bonos
   - Prestaciones

5. **⚙️ SERVICIOS**
   - Internet
   - Teléfono
   - Servicios profesionales

6. **🚗 TRANSPORTE**
   - Gasolina
   - Mantenimiento de vehículos
   - Reparaciones

7. **📦 OTRO**
   - Gastos no clasificados
   - Gastos extraordinarios

### Tab 2: Resumen

Visualiza gastos del período seleccionado:

```
┌─────────────────────────────────────────────────────────────┐
│ Desde: [2026-03-01]  Hasta: [2026-03-12]                   │
│                                                              │
│ 💸 Total Gastado    📝 Número de Gastos    📊 Promedio     │
│ $8,500.00           15                      $566.67         │
│                                                              │
│ ── Desglose por Categoría ──                                │
│                                                              │
│ 🔧 Refacciones - $3,500.00 (6 gastos)                      │
│ 👥 Empleados - $2,800.00 (4 gastos)                        │
│ 🚗 Transporte - $1,200.00 (3 gastos)                       │
│ ⚙️ Servicios - $1,000.00 (2 gastos)                        │
└─────────────────────────────────────────────────────────────┘
```

### Tab 3: Historial

Lista completa de gastos con opciones de:
- 🔍 Filtrar por fecha
- 🔍 Filtrar por categoría
- 🗑️ Eliminar gastos (con confirmación)

---

## 👥 Gestión de Usuarios

### Acceso

Navegación → **⚙️ Admin** → Tab **Usuarios**

### Crear Nuevo Usuario

```
┌─────────────────────────────────────────────────────────────┐
│ Username: [nuevo_operador]                                  │
│ Nombre completo: [Juan Pérez]                              │
│ Contraseña: [••••••••••]                                   │
│ Rol: [OPERADOR ▼]                                          │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Crear Usuario ]                              │
└─────────────────────────────────────────────────────────────┘
```

**Roles disponibles:**

1. **ADMIN** 👨‍💼
   - Acceso completo al sistema
   - Dashboard con métricas
   - Gestión de gastos
   - Configuración de usuarios, clientes, máquinas
   - Edición de cortes cerrados

2. **SUPERVISOR** 👨‍🏫
   - Operaciones de corte
   - Consulta de historial
   - Edición de cortes cerrados
   - NO puede gestionar usuarios ni gastos

3. **OPERADOR** 👨‍🔧
   - Operaciones de corte
   - Consulta de historial
   - NO puede editar cortes cerrados

### Editar Usuario Existente

1. Selecciona el usuario de la lista
2. Modifica los campos necesarios
3. Puedes cambiar:
   - Nombre
   - Rol
   - Estado (Activo/Inactivo)
   - Contraseña (opcional)

### Desactivar Usuario

**NO elimines usuarios**, mejor desactívalos:
1. Desmarca la casilla **"Activo"**
2. El usuario no podrá iniciar sesión
3. Su historial se mantiene intacto

---

## 🏢 Gestión de Clientes

### Acceso

Navegación → **⚙️ Admin** → Tab **Clientes**

### Crear Nuevo Cliente

```
┌─────────────────────────────────────────────────────────────┐
│ Nombre: [Tienda La Esquina]                                │
│ Comisión (%): [60.00]                                       │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Crear Cliente ]                              │
└─────────────────────────────────────────────────────────────┘
```

**Comisión (%):**
- Es el porcentaje que se queda la casa
- Ejemplo: 60% = Casa se queda con 60%, cliente recibe 40%
- Rango típico: 50% - 70%

### Editar Cliente

1. Selecciona el cliente de la lista
2. Puedes modificar:
   - Nombre
   - Porcentaje de comisión
   - Estado (Activo/Inactivo)

**⚠️ IMPORTANTE:**
- Cambiar la comisión NO afecta cortes anteriores
- Solo aplica a cortes nuevos

---

## 🎰 Gestión de Máquinas

### Acceso

Navegación → **⚙️ Admin** → Tab **Máquinas**

### Crear Nueva Máquina

```
┌─────────────────────────────────────────────────────────────┐
│ Código: [M-009]                                             │
│ Cliente: [Tienda La Esquina ▼]                             │
│ Contador Inicial: [0]                                       │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Crear Máquina ]                              │
└─────────────────────────────────────────────────────────────┘
```

**Campos:**
- **Código**: Identificador único (ej: M-001, M-002)
- **Cliente**: A quién pertenece la máquina
- **Contador Inicial**: Contador con el que inicia (usualmente 0)
- **Activo**: Si está en operación

### Editar Máquina

Puedes modificar:
- Código (con precaución)
- Cliente (si se mueve de ubicación)
- Estado (Activo/Inactivo)

**⚠️ NO modifiques el contador inicial** de máquinas en operación

### Desactivar Máquina

Cuando una máquina se retira:
1. Desmarca **"Activo"**
2. La máquina ya no aparecerá en cortes nuevos
3. Su historial se mantiene

---

## 🗺️ Configuración de Rutas

### Acceso

Navegación → **⚙️ Admin** → Tab **Rutas**

### Crear Nueva Ruta

```
┌─────────────────────────────────────────────────────────────┐
│ Nombre: [Ruta Centro]                                       │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Crear Ruta ]                                 │
└─────────────────────────────────────────────────────────────┘
```

### Asignar Usuarios a Rutas

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario: [Juan Pérez ▼]                                    │
│ Ruta: [Ruta Centro ▼]                                      │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Asignar ]                                     │
└─────────────────────────────────────────────────────────────┘
```

### Asignar Máquinas a Rutas

```
┌─────────────────────────────────────────────────────────────┐
│ Máquina: [M-005 ▼]                                         │
│ Ruta: [Ruta Centro ▼]                                      │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Asignar ]                                     │
└─────────────────────────────────────────────────────────────┘
```

**Beneficios de las rutas:**
- Organiza máquinas por zona geográfica
- Asigna operadores específicos a cada ruta
- Facilita la planificación de cortes

---

## 📚 Catálogos del Sistema

### Acceso

Navegación → **⚙️ Admin** → Tab **Catálogos**

### Tipos de Catálogos

#### 1. Irregularidades

Define tipos de problemas en máquinas:
- Máquina descompuesta
- Dinero faltante
- Contador alterado
- Vandalismo

#### 2. Omisiones

Razones para omitir una máquina:
- Local cerrado
- Sin acceso
- Máquina en mantenimiento

#### 3. Eventos de Contador

Eventos especiales:
- Reinicio de contador
- Cambio de máquina
- Ajuste manual

### Crear Entrada en Catálogo

```
┌─────────────────────────────────────────────────────────────┐
│ Nombre: [Máquina descompuesta]                             │
│ Requiere nota: ☑                                            │
│ Activo: ☑                                                   │
│                                                              │
│          [ ➕ Crear ]                                       │
└─────────────────────────────────────────────────────────────┘
```

**Requiere nota:**
- Si está marcado, el operador DEBE agregar una nota explicativa
- Útil para casos que necesitan documentación

---

## 📤 Exportación de Datos

### Acceso

Navegación → **📜 Historial** → Botón **"📥 Exportar a CSV"**

### Proceso de Exportación

1. Aplica los filtros deseados:
   - Cliente
   - Estado
   - Rango de fechas

2. Haz clic en **"📥 Exportar a CSV"**

3. Se descargará un archivo con:
   - Información de cortes
   - Detalle de máquinas
   - Montos y comisiones
   - Fechas y usuarios

### Uso del CSV

El archivo CSV puede abrirse en:
- Microsoft Excel
- Google Sheets
- Cualquier software de análisis de datos

**Columnas incluidas:**
- ID del corte
- Cliente
- Fecha
- Semana
- Estado
- Total capturado
- Comisión
- Pago al cliente
- Usuario que creó el corte

---

## ✅ Mejores Prácticas

### Seguridad

1. **Contraseñas**
   - Cambia la contraseña de admin inmediatamente
   - Usa contraseñas fuertes (mínimo 8 caracteres)
   - No compartas credenciales

2. **Usuarios**
   - Crea usuarios individuales para cada persona
   - Asigna el rol mínimo necesario
   - Desactiva usuarios que ya no trabajan

3. **Backups**
   - El sistema hace backups automáticos
   - Descarga backups manualmente cada semana
   - Guárdalos en un lugar seguro

### Operación

1. **Revisión Diaria**
   - Revisa el dashboard cada mañana
   - Verifica que los cortes del día anterior estén cerrados
   - Revisa gastos pendientes de registro

2. **Revisión Semanal**
   - Analiza tendencias de ingresos
   - Compara con semanas anteriores
   - Identifica máquinas con bajo rendimiento

3. **Revisión Mensual**
   - Cierra el mes contable
   - Exporta datos para contabilidad
   - Analiza gastos vs ingresos
   - Planifica el siguiente mes

### Mantenimiento

1. **Catálogos**
   - Mantén catálogos actualizados
   - Elimina entradas obsoletas
   - Agrega nuevas según necesidad

2. **Clientes y Máquinas**
   - Actualiza información de contacto
   - Desactiva máquinas retiradas
   - Documenta cambios importantes

3. **Usuarios**
   - Revisa permisos periódicamente
   - Actualiza roles según responsabilidades
   - Capacita a nuevos usuarios

### Análisis de Datos

1. **Indicadores Clave (KPIs)**
   - Ingreso promedio por máquina
   - Tasa de omisiones
   - Frecuencia de irregularidades
   - Gastos vs ingresos

2. **Reportes**
   - Genera reportes mensuales
   - Compara rendimiento por cliente
   - Identifica oportunidades de mejora

3. **Toma de Decisiones**
   - Usa datos para negociar comisiones
   - Identifica máquinas no rentables
   - Optimiza rutas de operadores

---

## 🚨 Situaciones Especiales

### Editar Corte Cerrado

Solo ADMIN y SUPERVISOR pueden hacerlo:

1. Ve al **Historial**
2. Busca el corte cerrado
3. Haz clic en **"✏️ Editar"**
4. Modifica lo necesario
5. Guarda los cambios

**⚠️ Usa con precaución:**
- Documenta por qué editaste el corte
- Informa al equipo de contabilidad
- Considera crear un nuevo corte si es posible

### Resolver Discrepancias

Si hay diferencias entre contador y dinero:

1. Documenta en las notas del corte
2. Investiga la causa
3. Registra como irregularidad si es necesario
4. Ajusta en el siguiente corte si aplica

### Cambio de Comisión

Si cambias el porcentaje de comisión de un cliente:

1. El cambio NO afecta cortes anteriores
2. Solo aplica a cortes nuevos
3. Documenta la fecha del cambio
4. Informa al cliente

---

## 📞 Soporte y Ayuda

### Recursos Disponibles

1. **Manuales**
   - Manual del Operador
   - Manual del Administrador (este documento)
   - Guía de Deployment

2. **Documentación Técnica**
   - README.md
   - MEJORAS_IMPLEMENTADAS.md

### Reportar Problemas

Si encuentras un error:

1. Anota qué estabas haciendo
2. Toma captura de pantalla del error
3. Documenta los pasos para reproducirlo
4. Contacta al soporte técnico

---

## 📊 Checklist del Administrador

### Diario
- [ ] Revisar dashboard
- [ ] Verificar cortes del día anterior
- [ ] Registrar gastos del día

### Semanal
- [ ] Analizar tendencias
- [ ] Revisar usuarios activos
- [ ] Verificar backups

### Mensual
- [ ] Exportar datos para contabilidad
- [ ] Analizar gastos vs ingresos
- [ ] Revisar rendimiento por cliente
- [ ] Actualizar catálogos si es necesario

---

**Versión del manual:** 1.0  
**Última actualización:** Marzo 2026

---

**¡Éxito en la administración de Zoreza! 📊**