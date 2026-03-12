# 🧾 Zoreza · Corte Semanal

Sistema de gestión de cortes semanales para máquinas expendedoras y recreativas. MVP funcional desarrollado con **Python + Streamlit** y **SQLite**, con arquitectura escalable y diseño moderno.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.33+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Características Principales

### 🎯 Gestión de Cortes
- **Cortes semanales** por cliente con estados BORRADOR/CERRADO
- **Captura de máquinas** con contadores y montos
- **Cálculo automático** de comisiones y pagos
- **Tickets térmicos** optimizados para impresoras de 80mm
- **Historial completo** con búsqueda y filtros avanzados

### 👥 Sistema de Roles (RBAC)
- **ADMIN**: Acceso completo + Dashboard + Gestión de gastos
- **SUPERVISOR**: Operaciones + Historial + Edición de cortes cerrados
- **OPERADOR**: Solo operaciones de corte

### 📊 Dashboard para Administradores
- Métricas del mes actual (Ingresos, Comisión, Gastos, Ganancia Neta)
- Comparación mensual con gráficas
- Distribución de gastos por categoría
- Accesos rápidos a funciones principales

### 💰 Gestión de Gastos
- 7 categorías: Refacciones, Fondos (Robos), Permisos, Empleados, Servicios, Transporte, Otro
- Registro detallado con fecha, monto, descripción y notas
- Resumen con totales y promedios
- Historial filtrable por fecha y categoría

### 🛠️ Funcionalidades Avanzadas
- **Exportación a CSV** de cortes e historial
- **Backup automático** de base de datos
- **Sistema de notificaciones** para irregularidades
- **Validaciones robustas** de entrada
- **Manejo centralizado de errores**
- **Búsqueda avanzada** con múltiples filtros

## 🚀 Deployment

### Streamlit Cloud (Recomendado)

1. **Sube el repositorio a GitHub**
2. **Conecta con Streamlit Cloud**:
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Conecta tu repositorio de GitHub
   - Selecciona `app.py` como archivo principal
3. **Deploy automático** ✅

### Otras Plataformas

#### Heroku
```bash
# Crear Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile
git push heroku main
```

#### Railway
```bash
# Railway detecta automáticamente Streamlit
railway up
```

#### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 💻 Instalación Local

### Requisitos
- Python 3.10 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/zoreza-corte-semanal.git
cd zoreza-corte-semanal

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -U pip
pip install -e .

# 4. (Opcional) Configurar variables de entorno
export APP_TZ=America/Mexico_City
export ZOREZA_DB_PATH=./data/zoreza.db

# 5. Inicializar base de datos
python -m zoreza.init_db

# 6. Ejecutar la aplicación
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

## 🔐 Credenciales Iniciales

**⚠️ IMPORTANTE: Cambia estas credenciales después del primer login**

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | ADMIN |
| operador | operador123 | OPERADOR |

Puedes cambiar usuarios y contraseñas en: **Admin → Usuarios**

## 📁 Estructura del Proyecto

```
zoreza-corte-semanal/
├── app.py                      # Punto de entrada de Streamlit
├── requirements.txt            # Dependencias Python
├── pyproject.toml             # Configuración del proyecto
├── .gitignore                 # Archivos ignorados por Git
├── .streamlit/
│   └── config.toml            # Configuración de Streamlit
├── data/
│   └── zoreza.db              # Base de datos SQLite (auto-generada)
├── zoreza/
│   ├── __init__.py
│   ├── init_db.py             # Inicialización de BD
│   ├── db/                    # Capa de datos
│   │   ├── core.py            # Esquema y conexión
│   │   ├── queries.py         # Queries SQL
│   │   └── repo.py            # Repositorio (CRUD)
│   ├── services/              # Lógica de negocio
│   │   ├── auth.py            # Autenticación
│   │   ├── rbac.py            # Control de acceso
│   │   ├── calculations.py    # Cálculos de cortes
│   │   ├── validations.py     # Validaciones
│   │   ├── time_utils.py      # Utilidades de tiempo
│   │   ├── exceptions.py      # Excepciones personalizadas
│   │   ├── error_handler.py   # Manejo de errores
│   │   ├── export_service.py  # Exportación CSV
│   │   ├── backup_service.py  # Backups automáticos
│   │   └── dashboard_service.py # Métricas y estadísticas
│   ├── ticket/                # Generación de tickets
│   │   └── render.py          # Renderizado HTML/CSS
│   └── ui/                    # Interfaz de usuario
│       ├── app_shell.py       # Shell principal
│       ├── components/        # Componentes reutilizables
│       └── pages/             # Páginas de la app
│           ├── operacion_corte.py
│           ├── historial.py
│           ├── admin.py
│           ├── dashboard.py
│           └── gastos.py
└── MEJORAS_IMPLEMENTADAS.md   # Documentación de mejoras
```

## 🎨 Diseño y UX

- **Tema oscuro** con colores corporativos (naranja/dorado #FF8C42)
- **Navegación intuitiva** con iconos y efectos hover
- **Diseño responsive** adaptable a diferentes pantallas
- **Feedback visual** claro para todas las acciones
- **Botones estilizados** con gradientes y sombras

## 🔧 Configuración

### Variables de Entorno

```bash
# Zona horaria (default: America/Mexico_City)
export APP_TZ=America/Mexico_City

# Ruta de la base de datos (default: ./data/zoreza.db)
export ZOREZA_DB_PATH=./data/zoreza.db
```

### Configuración de Streamlit

Edita `.streamlit/config.toml` para personalizar:
- Colores del tema
- Puerto del servidor
- Configuraciones de seguridad

## 📊 Base de Datos

### Esquema Principal

- **usuarios**: Gestión de usuarios y roles
- **clientes**: Clientes con porcentaje de comisión
- **maquinas**: Máquinas por cliente
- **rutas**: Rutas de operación
- **cortes**: Cortes semanales (BORRADOR/CERRADO)
- **corte_detalle**: Detalle de cada máquina en el corte
- **gastos**: Registro de gastos del negocio
- **Catálogos**: Irregularidades, omisiones, eventos

### Reglas de Negocio

- **1 corte por semana por cliente**: `UNIQUE(cliente_id, week_start)`
- **Semana**: Lunes 00:00:00 a Domingo 23:59:59
- **Estados**: BORRADOR (editable) → CERRADO (solo lectura*)
- **Permisos**: ADMIN puede editar cortes cerrados

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Mario López**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Streamlit por el excelente framework
- La comunidad de Python por las herramientas

---

**Hecho con ❤️ y ☕ en México**
