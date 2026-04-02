# Infraestructura — Zoreza Labs (Producción)

Guía completa para desplegar todo el ecosistema Zoreza Labs con el **menor costo posible**,
manteniendo un servicio profesional listo para facturar.

---

## Resumen de servicios necesarios

| Componente          | Servicio recomendado          | Costo mensual  |
|---------------------|-------------------------------|----------------|
| **Dominio** (.mx)   | Cloudflare Registrar          | ~$250 MXN/año  |
| **DNS + CDN + SSL** | Cloudflare (Free)             | $0             |
| **Servidor (VPS)**  | Oracle Cloud Free Tier (ARM)  | $0             |
| **Túnel seguro**    | Cloudflare Tunnel (Free)      | $0             |
| **Web frontend**    | Cloudflare Pages (Free)       | $0             |
| **Email corporativo** | Cloudflare Email Routing    | $0             |
| **Backups**         | Cloudflare R2 (Free tier)     | $0             |
| **TOTAL**           |                               | **~$250 MXN/año** |

> **Nota**: Si Oracle Cloud no está disponible en tu región, alternativas económicas son
> Hetzner (~€4.5/mes), DigitalOcean ($4/mes), o Vultr ($3.50/mes).

---

## 1. Dominio — Cloudflare Registrar

1. Crear cuenta en [Cloudflare](https://dash.cloudflare.com/sign-up)
2. Ir a **Registrar Dominios** → Buscar `zorezalabs.mx`
3. Registrar (precio al costo, sin markup)
4. El DNS se configura automáticamente en Cloudflare

**Costo**: ~$250 MXN/año (precio at-cost de Cloudflare para .mx)

---

## 2. Servidor (VPS) — Oracle Cloud Free Tier

Oracle Cloud ofrece **GRATIS para siempre** una VM ARM con specs generosos:

- **4 OCPU** (ARM Ampere A1)
- **24 GB RAM**
- **200 GB** almacenamiento
- **Tráfico**: 10 TB/mes de egress incluido

### Pasos:

1. Crear cuenta en [Oracle Cloud](https://cloud.oracle.com/free)
   - Requiere tarjeta de crédito (no cobra mientras sea Free Tier)
2. Ir a **Compute → Instances → Create Instance**
3. Configurar:
   - **Shape**: VM.Standard.A1.Flex (ARM)
   - **OCPU**: 2 (suficiente para tu uso)
   - **RAM**: 12 GB
   - **Image**: Ubuntu 22.04 (ARM)
   - **Boot volume**: 50 GB
4. Descargar la SSH key y conectarse:
   ```bash
   ssh -i ~/clave-oracle.key ubuntu@<IP_PUBLICA>
   ```

### Instalar dependencias en la VM:

```bash
# Python 3.11+
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip git

# Node.js 20 (para builds del frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Crear directorio del proyecto
sudo mkdir -p /opt/zoreza && sudo chown $USER:$USER /opt/zoreza
cd /opt/zoreza
git clone https://github.com/zoreza/zoreza-corte-semanal.git .
```

### Configurar backend:

```bash
cd /opt/zoreza/zoreza-pro/backend

# Entorno virtual
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Archivo de configuración
cat > .env << 'EOF'
APP_NAME=Zoreza Pro
DEBUG=false
SECRET_KEY=$(openssl rand -hex 64)
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
EOF

# Crear directorios de datos
mkdir -p data/tenants data/releases data/backups

# Probar que arranca
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Servicio systemd (auto-start):

```bash
sudo tee /etc/systemd/system/zoreza.service << 'EOF'
[Unit]
Description=Zoreza Pro Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/zoreza/zoreza-pro/backend
Environment=PATH=/opt/zoreza/zoreza-pro/backend/venv/bin:/usr/bin
ExecStart=/opt/zoreza/zoreza-pro/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable zoreza
sudo systemctl start zoreza
sudo systemctl status zoreza
```

---

## 3. Cloudflare Tunnel (exponer el servidor sin abrir puertos)

### Instalar cloudflared en la VM:

```bash
# ARM64
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Autenticar
cloudflared login
# Esto abre un link — autenticarse con la cuenta Cloudflare donde está el dominio
```

### Crear el túnel:

```bash
cloudflared tunnel create zoreza-prod

# Configurar
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: zoreza-prod
credentials-file: /home/ubuntu/.cloudflared/<TUNNEL_ID>.json

ingress:
  # Backend API — todas las rutas /{slug}/api y /zoreza-admin/api
  - hostname: zorezalabs.mx
    service: http://127.0.0.1:8000
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF

# Crear DNS record
cloudflared tunnel route dns zoreza-prod zorezalabs.mx
```

### Servicio systemd para el túnel:

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### ¿Y el frontend web?

Hay dos opciones:

**Opción A: Servir desde el mismo backend (más simple)**

Agregar a `main.py` un mount de archivos estáticos para servir el build de React:
```python
from fastapi.staticfiles import StaticFiles
# Después de las rutas API:
app.mount("/", StaticFiles(directory="web-dist", html=True), name="static")
```

Luego en deploy:
```bash
cd /opt/zoreza/zoreza-pro/web
npm ci && npm run build
cp -r dist/ ../backend/web-dist/
```

**Opción B: Cloudflare Pages (recomendado para producción)**

---

## 4. Web Frontend — Cloudflare Pages (Opción B)

Cloudflare Pages sirve sitios estáticos gratis con CDN global.

### Configurar:

1. En Cloudflare Dashboard → **Pages** → **Create a project**
2. Conectar repositorio de GitHub (`zoreza/zoreza-corte-semanal`)
3. Configurar build:
   - **Root directory**: `zoreza-pro/web`
   - **Build command**: `npm run build`
   - **Output directory**: `dist`
4. **Environment variables**:
   - `VITE_API_URL` = `https://zorezalabs.mx` (o vacío si es mismo dominio)
5. Dominio personalizado:
   - Settings → Custom Domains → Agregar `app.zorezalabs.mx`
   - O usar el mismo `zorezalabs.mx` con route rules

> **Nota**: Si usas Cloudflare Pages en un subdominio (app.zorezalabs.mx),
> necesitas ajustar el proxy de Vite o las URLs de API para que apunten al 
> dominio principal (zorezalabs.mx) donde está el backend.

**La opción más simple es la A** — servir todo desde el mismo dominio con el backend.
Así no hay problemas de CORS y la configuración es mínima.

---

## 5. Email Corporativo — Cloudflare Email Routing

Para poder enviar/recibir email desde `contacto@zorezalabs.mx` **sin pagar**:

### Recibir email (gratis):
1. Cloudflare Dashboard → **Email** → **Email Routing**
2. Agregar ruta: `contacto@zorezalabs.mx` → tu email personal (Gmail, etc.)
3. También puedes configurar catch-all: `*@zorezalabs.mx` → tu email

### Enviar email (para facturas/notificaciones):
- **Opción gratuita**: [Resend](https://resend.com) — 3,000 emails/mes gratis
- Configurar dominio con SPF/DKIM en Cloudflare DNS
- Usar la API de Resend desde el backend si necesitas enviar notificaciones

---

## 6. Backups — Cloudflare R2

R2 es el almacenamiento de objetos de Cloudflare. Free tier generoso:
- **10 GB** almacenamiento
- **10 millones** operaciones Class A/mes
- **Sin costos de egress**

### Configurar backup automático:

```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar R2
rclone config
# Tipo: s3
# Provider: Cloudflare
# Endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
# Access key + Secret: obtener desde Cloudflare Dashboard → R2 → Manage API tokens

# Script de backup
cat > /opt/zoreza/backup.sh << 'SCRIPT'
#!/bin/bash
set -e
BACKUP_DIR="/tmp/zoreza-backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Copiar DBs
cp /opt/zoreza/zoreza-pro/backend/data/master.db "$BACKUP_DIR/"
cp /opt/zoreza/zoreza-pro/backend/data/tenants/*.db "$BACKUP_DIR/"

# Comprimir
tar czf "${BACKUP_DIR}.tar.gz" -C /tmp "$(basename $BACKUP_DIR)"

# Subir a R2
rclone copy "${BACKUP_DIR}.tar.gz" r2:zoreza-backups/

# Limpiar
rm -rf "$BACKUP_DIR" "${BACKUP_DIR}.tar.gz"

# Mantener solo últimos 30 backups
rclone delete r2:zoreza-backups/ --min-age 30d

echo "Backup completado: $(date)"
SCRIPT
chmod +x /opt/zoreza/backup.sh

# Cron diario a las 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/zoreza/backup.sh >> /var/log/zoreza-backup.log 2>&1") | crontab -
```

---

## 7. Facturación

Para que el servicio pueda facturar (emitir CFDI en México):

### Opciones económicas:

| Servicio | Costo | Notas |
|----------|-------|-------|
| **Factura.com** | Desde $149/mes | API REST, fácil de integrar |
| **SWsapien** | ~$100/mes base | Popular en México |
| **Finkok** (sandbox gratis) | Por timbrado (~$2-4 MXN c/u) | Pago por uso |

**Recomendación**: Empezar con **Finkok** (pago por uso).
Con 3-4 tenants, serían ~4-12 facturas/mes = ~$24-48 MXN/mes.

Esto se integraría como un módulo futuro en el backend si lo necesitas.

---

## 8. Actualizaciones de la App Android

El sistema de auto-actualización ya está implementado. El flujo es:

### Publicar nueva versión:

1. Compilar APK en desarrollo:
   ```bash
   cd zoreza-pro/app
   # Incrementar version en pubspec.yaml (version: 1.1.0+2)
   flutter build apk --release
   ```

2. Ir al panel **Super Admin** → **App Releases** → **Subir APK**
   - Versión: `1.1.0`
   - Código: `2` (debe ser mayor al anterior)
   - Notas de la versión: "Mejoras de rendimiento..."
   - Seleccionar el archivo APK
   - Marcar como obligatoria si es crítica

3. La app Android **detecta automáticamente** la nueva versión al iniciar
   y muestra un diálogo al usuario para actualizar.

### Flujo del usuario:
1. Abre la app → aparece diálogo "Actualización disponible v1.1.0"
2. Toca "Actualizar" → se descarga con barra de progreso
3. Al terminar → Android abre la pantalla de instalación
4. El usuario toca "Instalar" → listo

> **Importante**: Los usuarios deben tener habilitada la opción
> **"Instalar apps de fuentes desconocidas"** para la app Zoreza Pro.
> La primera vez Android les pedirá habilitarlo.

---

## Arquitectura final

```
                    ┌─────────────────────────────┐
                    │       Cloudflare DNS         │
                    │    zorezalabs.mx (Proxied)   │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │    Cloudflare Tunnel         │
                    │    (Encriptado, sin IP exp.) │
                    └────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────────┐
                    │    Oracle Cloud VM (ARM)     │
                    │    Ubuntu 22.04              │
                    │                              │
                    │  ┌──────────────────────┐    │
                    │  │  Uvicorn (port 8000)  │    │
                    │  │  FastAPI Backend      │    │
                    │  │  + Static Web Files   │    │
                    │  └──────────┬───────────┘    │
                    │             │                 │
                    │  ┌──────────▼───────────┐    │
                    │  │  SQLite Databases     │    │
                    │  │  master.db            │    │
                    │  │  tenants/demo.db      │    │
                    │  │  tenants/cliente1.db  │    │
                    │  └──────────────────────┘    │
                    │                              │
                    │  data/releases/              │
                    │   └── zoreza-pro-v1.0.0.apk  │
                    └──────────────────────────────┘

    Clientes acceden vía:
    📱 App Android → https://zorezalabs.mx/{tenant}/api/v1/...
    💻 Web Admin  → https://zorezalabs.mx/{tenant}/
    ⚡ Super Admin → https://zorezalabs.mx/zoreza-admin/
```

---

## Checklist de despliegue

- [ ] Registrar dominio zorezalabs.mx en Cloudflare
- [ ] Crear VM en Oracle Cloud (Ubuntu ARM)
- [ ] Instalar Python 3.11, Node 20, git en la VM
- [ ] Clonar repositorio y configurar backend (.env, venv)
- [ ] Build del web frontend y copiar a web-dist/
- [ ] Crear servicio systemd para el backend
- [ ] Instalar y configurar Cloudflare Tunnel
- [ ] Configurar Email Routing en Cloudflare
- [ ] Configurar backup automático con R2
- [ ] Subir primera versión del APK desde Super Admin
- [ ] Generar SECRET_KEY seguro: `openssl rand -hex 64`
- [ ] Cambiar contraseña del super-admin por defecto
- [ ] Probar flujo completo: web + app + auto-update

---

## Costos totales estimados

### Primer mes:
| Concepto | Costo |
|----------|-------|
| Dominio .mx (anual) | ~$250 MXN |
| Servidor Oracle | $0 |
| Cloudflare (DNS, CDN, Tunnel, Pages, R2, Email) | $0 |
| **Total primer año** | **~$250 MXN (~$15 USD)** |

### Escenarios de crecimiento:

| Escala | Solución | Costo adicional |
|--------|----------|----------------|
| 1-10 tenants | Oracle Free VM | $0 |
| 10-50 tenants | Migrar a Hetzner CX22 | ~€4.5/mes |
| 50+ tenants | Hetzner CX32 + PostgreSQL | ~€9/mes |

Con SQLite y 3-4 usuarios concurrentes, Oracle Free Tier es más que suficiente.
