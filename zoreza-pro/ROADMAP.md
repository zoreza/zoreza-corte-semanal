# Zoreza Pro — Roadmap de Releases

> Documento vivo. Actualizar conforme avancen las fases.

---

## Filosofía de Versionado

```
MAYOR.MENOR.PARCHE   Ejemplo: 1.2.3
  │     │     └─ Hotfix / PTF (Program Temporary Fix)
  │     └─ Feature release menor
  └─ Release mayor (breaking changes o hitos grandes)
```

- **PTF / Hotfix** (1.0.x): Correcciones urgentes en producción. Se aplican sobre la rama `main` con cherry-pick.
- **Minor** (1.x.0): Nuevas features que no rompen compatibilidad.
- **Major** (x.0.0): Cambios arquitecturales o de breaking changes.

---

## v1.0.0 — "Lanzamiento Oficial"

**Objetivo**: Sistema estable, probado y listo para producción con las funcionalidades core.

### Estado Actual ✅

| Feature | Estado |
|---------|--------|
| Backend FastAPI multi-tenant | ✅ Completo |
| Base de datos SQLite (una por tenant) | ✅ Completo |
| JWT Auth (access + refresh tokens) | ✅ Completo |
| **Passkey / WebAuthn** | ✅ Implementado |
| CRUD: Clientes, Máquinas, Rutas, Usuarios | ✅ Completo |
| Cortes semanales con cálculos automáticos | ✅ Completo |
| Gastos por categoría | ✅ Completo |
| Catálogos dinámicos (irregularidad, omisión, evento) | ✅ Completo |
| Dashboard con gráficas | ✅ Completo |
| Exportar a Excel | ✅ Completo |
| Sync offline-first (push/pull) | ✅ Completo |
| Ticket térmico Bluetooth (ESC/POS) | ✅ Completo |
| Auto-update APK | ✅ Completo |
| Super Admin: gestión de tenants y releases | ✅ Completo |
| Web admin con tema oscuro | ✅ Completo |
| Sitio de descarga de APK | ✅ Completo |
| Documentación PROJECT.md (AI-readable) | ✅ Completo |
| Manuales de usuario (App, Web, SuperAdmin) | ✅ Completo |

### Pendiente para v1.0.0 Release

| Tarea | Prioridad | Estimación |
|-------|-----------|-----------|
| Pruebas end-to-end manuales (flujo completo) | 🔴 Alta | — |
| Test de sincronización offline → online | 🔴 Alta | — |
| Hardcodear secret_key de producción vía env | 🔴 Alta | — |
| Configurar HTTPS (Cloudflare o Let's Encrypt) | 🔴 Alta | — |
| Primer APK release compilado y subido | 🔴 Alta | — |
| Crear primer tenant de producción | 🔴 Alta | — |
| Validar impresión térmica en hardware real | 🟡 Media | — |
| Smoke test en dispositivo Android real | 🟡 Media | — |
| Backup automático de bases de datos | 🟡 Media | — |
| Rate limiting en endpoints de auth | 🟢 Baja | — |

### Criterios de Lanzamiento v1.0

- [ ] Un operador puede completar un corte semanal completo (crear → capturar → cerrar → imprimir ticket)
- [ ] Sincronización funciona correctamente offline → online
- [ ] Login funciona con contraseña y con passkey
- [ ] Web admin permite gestionar todo el catálogo
- [ ] Super admin puede crear tenants y subir APKs
- [ ] El APK se auto-actualiza correctamente
- [ ] Datos correctos en dashboard (recaudación, gastos, neto)

---

## v1.0.x — PTFs (Program Temporary Fixes)

Hotfixes que pueden surgir después del lanzamiento:

| Escenario | Acción |
|-----------|--------|
| Bug crítico en cálculo de comisiones | PTF inmediato, bump a 1.0.1 |
| Crash en sincronización con datos huérfanos | PTF, verificar integridad de UUIDs |
| Problema de permisos en Android para APK install | PTF, ajustar AndroidManifest |
| Token refresh loop en app | PTF, validar estado de refresh token |
| Passkey no funciona en ciertos dispositivos | PTF, fallback graceful a contraseña |
| Error de migración al crear nuevo tenant | PTF, validar schema creation |

**Proceso de PTF:**
1. Reportar issue en GitHub
2. Crear branch `hotfix/1.0.x-descripcion`
3. Fix + test manual
4. Merge a `main`, tag `v1.0.x`
5. Si es app: subir nuevo APK via Super Admin
6. Si es backend/web: redeploy en servidor

---

## v1.1.0 — "Calidad de Vida"

**Objetivo**: Mejoras de usabilidad basadas en feedback real de operadores en campo.

| Feature | Descripción |
|---------|------------|
| 🔔 Notificaciones push | Firebase Cloud Messaging para alertas de cortes pendientes |
| 📷 Fotos de evidencia | Adjuntar fotos al capturar máquinas (evidencia de contadores) |
| 📝 Notas de corte | Campo de notas generales por corte |
| 🗺️ Orden de visita en ruta | Definir secuencia de máquinas en una ruta |
| 📊 Filtros avanzados en dashboard | Por ruta, por operador, comparativo semanal |
| 🔍 Búsqueda global | Buscar cliente/máquina/corte desde cualquier pantalla |
| 📱 Widget de Android | Widget de acceso rápido al último corte pendiente |

---

## v1.2.0 — "Reportes Profesionales"

| Feature | Descripción |
|---------|------------|
| 📄 PDF de corte | Generar PDF del corte individual con detalle por máquina |
| 📊 Reporte mensual | PDF consolidado mensual (recaudación, gastos, comisiones) |
| 📧 Email automático | Enviar PDF del corte al email del cliente automáticamente |
| 📈 Gráficas comparativas | Tendencias por máquina individual a lo largo del tiempo |
| 🧾 Historial de tickets | Reimpresión de tickets pasados |

---

## v2.0.0 — "Escala Empresarial"

**Objetivo**: Arquitectura robusta para soportar alto volumen y funcionalidades empresariales.

| Feature | Descripción | Impacto |
|---------|------------|---------|
| 🐘 **PostgreSQL** | Migración de SQLite a PostgreSQL para concurrencia real | Alto |
| 🔄 **Sync bidireccional real-time** | WebSockets para sincronización inmediata | Alto |
| 🏢 **Multi-sucursal** | Un tenant puede tener múltiples ubicaciones | Alto |
| 👥 **Permisos granulares** | RBAC con permisos por recurso (ver solo mis rutas) | Medio |
| 🌐 **PWA** | App web como PWA instalable (alternativa ligera al APK) | Medio |
| 📦 **Inventario de máquinas** | Tracking de vida útil, mantenimientos, refacciones | Medio |
| 💳 **Integración de pagos** | Pagos electrónicos de comisiones a clientes | Alto |
| 🤖 **IA analítica** | Predicción de recaudación, detección de anomalías | Bajo |
| 🏗️ **CI/CD** | GitHub Actions: lint, test, build APK, deploy automático | Alto |
| 🧪 **Test suite** | Tests unitarios + integración + E2E (>80% coverage) | Alto |
| 📱 **iOS** | Versión para iPhone (Flutter ya es cross-platform) | Medio |

### Breaking Changes en v2.0

- Schema de BD: migración de SQLite a PostgreSQL con Alembic
- URLs de API: posible cambio del prefix de versionado a `/api/v2/`
- Sync protocol: cambio de pull/push manual a WebSocket streaming
- Auth: posible integración con proveedor externo (Auth0 / Supabase)

### Prerequisitos para v2.0

1. Base de usuarios activos en v1.x (feedback real)
2. CI/CD configurado y funcionando
3. Suite de tests con cobertura mínima de 80%
4. Plan de migración de datos documentado y probado
5. Infraestructura de staging separada de producción

---

## Pipeline de Desarrollo

```
Feature Branch       PR / Review        Main Branch         Production
    │                    │                  │                    │
    ├──► develop ──────► code review ──────► merge ──────────► deploy
    │                    │                  │                    │
    │              lint + build check  tag version           APK upload
    │                                 git tag v1.x.x        server restart
```

### Convenciones de Commits

```
feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato (no afecta lógica)
refactor: reestructuración sin cambio de comportamiento
test: agregar o modificar tests
chore: mantenimiento, dependencias, CI
```

### Release Checklist

- [ ] Todos los tests pasan (cuando existan)
- [ ] Build de web genera sin errores
- [ ] Build de APK compila sin errores
- [ ] Backend inicia sin errores
- [ ] Changelog actualizado
- [ ] Tag de git creado
- [ ] APK subido al sistema de releases
- [ ] Servidor desplegado
- [ ] Smoke test post-deploy

---

## Contacto

**Zoreza Labs** — Desarrollo de software a medida
- 🌐 zorezalabs.mx
- 📧 contacto@zorezalabs.mx
