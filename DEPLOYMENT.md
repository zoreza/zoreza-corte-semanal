# 🚀 Guía de Deployment

Esta guía te ayudará a deployar **Zoreza · Corte Semanal** en diferentes plataformas.

## 📋 Tabla de Contenidos

- [Streamlit Cloud (Recomendado)](#streamlit-cloud-recomendado)
- [Heroku](#heroku)
- [Railway](#railway)
- [Docker](#docker)
- [VPS/Servidor Propio](#vpsservidor-propio)

---

## Streamlit Cloud (Recomendado)

### ✅ Ventajas
- **Gratis** para proyectos públicos
- **Deploy automático** desde GitHub
- **SSL incluido** (HTTPS)
- **Fácil de configurar**
- **Actualizaciones automáticas** al hacer push

### 📝 Pasos

1. **Sube tu código a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/tu-usuario/zoreza-corte-semanal.git
   git push -u origin main
   ```

2. **Conecta con Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con tu cuenta de GitHub
   - Click en "New app"
   - Selecciona tu repositorio
   - Branch: `main`
   - Main file path: `app.py`
   - Click en "Deploy!"

3. **Configuración (Opcional)**
   - En "Advanced settings" puedes configurar:
     - Python version: `3.10`
     - Secrets (si necesitas variables de entorno)

4. **¡Listo!** 🎉
   - Tu app estará disponible en: `https://tu-usuario-zoreza-corte-semanal.streamlit.app`

### 🔐 Secrets (Variables de Entorno)

Si necesitas configurar variables de entorno:

1. En Streamlit Cloud, ve a tu app
2. Click en "⋮" → "Settings" → "Secrets"
3. Agrega tus secrets en formato TOML:
   ```toml
   APP_TZ = "America/Mexico_City"
   ZOREZA_DB_PATH = "./data/zoreza.db"
   ```

---

## Heroku

### 📝 Pasos

1. **Instala Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Descarga desde https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Crea un Procfile**
   ```bash
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   ```

3. **Crea setup.sh** (para configurar Streamlit)
   ```bash
   cat > setup.sh << 'EOF'
   mkdir -p ~/.streamlit/
   echo "\
   [server]\n\
   headless = true\n\
   port = $PORT\n\
   enableCORS = false\n\
   \n\
   " > ~/.streamlit/config.toml
   EOF
   ```

4. **Deploy**
   ```bash
   heroku login
   heroku create tu-app-zoreza
   git push heroku main
   heroku open
   ```

### 💰 Costo
- **Free tier**: Disponible pero con limitaciones
- **Hobby**: $7/mes
- **Professional**: $25-50/mes

---

## Railway

### 📝 Pasos

1. **Instala Railway CLI** (opcional)
   ```bash
   npm i -g @railway/cli
   ```

2. **Deploy desde GitHub**
   - Ve a [railway.app](https://railway.app)
   - Click en "Start a New Project"
   - Selecciona "Deploy from GitHub repo"
   - Selecciona tu repositorio
   - Railway detectará automáticamente que es una app Streamlit

3. **Configuración automática**
   - Railway detecta `requirements.txt`
   - Configura el comando de inicio automáticamente
   - Asigna un dominio público

### 💰 Costo
- **Free tier**: $5 de crédito mensual
- **Developer**: $10/mes
- **Team**: $20/mes

---

## Docker

### 📝 Dockerfile

Crea un archivo `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements.txt .
COPY pyproject.toml .
COPY app.py .
COPY zoreza/ zoreza/
COPY .streamlit/ .streamlit/

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Crear directorio para datos
RUN mkdir -p data

# Exponer puerto
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando de inicio
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 🏗️ Build y Run

```bash
# Build
docker build -t zoreza-corte-semanal .

# Run
docker run -p 8501:8501 zoreza-corte-semanal

# Run con volumen para persistencia
docker run -p 8501:8501 -v $(pwd)/data:/app/data zoreza-corte-semanal
```

### 🐙 Docker Compose

Crea `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - APP_TZ=America/Mexico_City
    restart: unless-stopped
```

Ejecutar:
```bash
docker-compose up -d
```

---

## VPS/Servidor Propio

### 📝 Pasos (Ubuntu/Debian)

1. **Actualizar sistema**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Instalar Python 3.10+**
   ```bash
   sudo apt install python3.10 python3.10-venv python3-pip -y
   ```

3. **Clonar repositorio**
   ```bash
   git clone https://github.com/tu-usuario/zoreza-corte-semanal.git
   cd zoreza-corte-semanal
   ```

4. **Configurar entorno virtual**
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

5. **Crear servicio systemd**
   ```bash
   sudo nano /etc/systemd/system/zoreza.service
   ```

   Contenido:
   ```ini
   [Unit]
   Description=Zoreza Corte Semanal
   After=network.target

   [Service]
   Type=simple
   User=tu-usuario
   WorkingDirectory=/home/tu-usuario/zoreza-corte-semanal
   Environment="PATH=/home/tu-usuario/zoreza-corte-semanal/.venv/bin"
   ExecStart=/home/tu-usuario/zoreza-corte-semanal/.venv/bin/streamlit run app.py --server.port=8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Iniciar servicio**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable zoreza
   sudo systemctl start zoreza
   sudo systemctl status zoreza
   ```

7. **Configurar Nginx (opcional)**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/zoreza
   ```

   Contenido:
   ```nginx
   server {
       listen 80;
       server_name tu-dominio.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

   Activar:
   ```bash
   sudo ln -s /etc/nginx/sites-available/zoreza /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **SSL con Let's Encrypt (opcional)**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d tu-dominio.com
   ```

---

## 🔒 Seguridad

### Recomendaciones

1. **Cambia las credenciales por defecto** inmediatamente después del deployment
2. **Usa HTTPS** siempre que sea posible
3. **Configura backups automáticos** de la base de datos
4. **Limita el acceso** por IP si es posible
5. **Mantén las dependencias actualizadas**

### Variables de Entorno Sensibles

Nunca subas a GitHub:
- Contraseñas
- API keys
- Tokens de acceso
- Información sensible

Usa `.env` o secrets de la plataforma.

---

## 📊 Monitoreo

### Streamlit Cloud
- Dashboard integrado con métricas de uso
- Logs en tiempo real
- Alertas por email

### Otras Plataformas
- Usa herramientas como:
  - **Sentry** para errores
  - **Datadog** para métricas
  - **Uptime Robot** para disponibilidad

---

## 🆘 Troubleshooting

### Error: "Module not found"
```bash
pip install -r requirements.txt
pip install -e .
```

### Error: "Database locked"
- Asegúrate de que solo una instancia accede a la BD
- Usa volúmenes persistentes en Docker

### Error: "Port already in use"
```bash
# Cambiar puerto
streamlit run app.py --server.port=8502
```

### La app se reinicia constantemente
- Revisa los logs: `streamlit run app.py --logger.level=debug`
- Verifica memoria disponible
- Aumenta recursos del servidor

---

## 📞 Soporte

Si tienes problemas con el deployment:
1. Revisa los logs de la plataforma
2. Consulta la documentación oficial
3. Abre un issue en GitHub

---

**¡Buena suerte con tu deployment! 🚀**