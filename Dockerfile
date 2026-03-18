# Dockerfile para Railway
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt pyproject.toml ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Instalar el paquete en modo editable
RUN pip install -e .

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Configurar Streamlit
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Crear script de inicio que maneja el puerto dinámico
RUN echo '#!/bin/bash\n\
# Railway proporciona PORT, usar 8501 como fallback\n\
PORT=${PORT:-8501}\n\
echo "Starting Streamlit on port $PORT"\n\
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Comando para ejecutar la aplicación
CMD ["/app/start.sh"]