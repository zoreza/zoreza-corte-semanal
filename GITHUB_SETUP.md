# 📦 Guía para Subir a GitHub

Esta guía te ayudará a subir tu proyecto **Zoreza · Corte Semanal** a GitHub paso a paso.

## 🚀 Pasos Rápidos

### 1. Inicializar Git (si no está inicializado)

```bash
git init
```

### 2. Agregar todos los archivos

```bash
git add .
```

### 3. Hacer el primer commit

```bash
git commit -m "Initial commit: Zoreza Corte Semanal MVP"
```

### 4. Crear repositorio en GitHub

1. Ve a [github.com](https://github.com)
2. Click en el botón **"+"** (arriba derecha) → **"New repository"**
3. Nombre del repositorio: `zoreza-corte-semanal`
4. Descripción: `Sistema de gestión de cortes semanales para máquinas expendedoras`
5. **NO** marques "Initialize this repository with a README" (ya tienes uno)
6. Click en **"Create repository"**

### 5. Conectar con el repositorio remoto

```bash
# Reemplaza 'tu-usuario' con tu nombre de usuario de GitHub
git remote add origin https://github.com/tu-usuario/zoreza-corte-semanal.git
```

### 6. Renombrar rama a 'main' (si es necesario)

```bash
git branch -M main
```

### 7. Subir el código

```bash
git push -u origin main
```

## ✅ Verificación

Después de hacer push, verifica en GitHub que todos los archivos se subieron correctamente:

- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `LICENSE`
- ✅ Carpeta `zoreza/`
- ✅ Carpeta `.streamlit/`

**IMPORTANTE:** La carpeta `data/` y archivos `.db` NO deben aparecer (están en `.gitignore`)

## 🔄 Comandos Git Útiles

### Ver estado de los archivos

```bash
git status
```

### Ver historial de commits

```bash
git log --oneline
```

### Agregar cambios específicos

```bash
git add archivo.py
git add carpeta/
```

### Hacer commit con mensaje descriptivo

```bash
git commit -m "Descripción clara del cambio"
```

### Subir cambios

```bash
git push
```

### Descargar cambios del repositorio

```bash
git pull
```

### Ver diferencias antes de commit

```bash
git diff
```

### Deshacer cambios no commiteados

```bash
git checkout -- archivo.py
```

### Crear una nueva rama

```bash
git checkout -b nombre-rama
```

### Cambiar de rama

```bash
git checkout main
```

### Fusionar rama

```bash
git checkout main
git merge nombre-rama
```

## 🏷️ Tags y Releases

### Crear un tag para versión

```bash
git tag -a v1.0.0 -m "Primera versión estable"
git push origin v1.0.0
```

### Listar tags

```bash
git tag
```

### Crear Release en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **"Releases"** → **"Create a new release"**
3. Selecciona el tag `v1.0.0`
4. Título: `v1.0.0 - Primera Versión Estable`
5. Descripción: Lista de características principales
6. Click en **"Publish release"**

## 🔐 Configuración de SSH (Opcional pero Recomendado)

### 1. Generar clave SSH

```bash
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"
```

### 2. Agregar clave al ssh-agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### 3. Copiar clave pública

```bash
# macOS
pbcopy < ~/.ssh/id_ed25519.pub

# Linux
cat ~/.ssh/id_ed25519.pub
# Copia manualmente el output
```

### 4. Agregar a GitHub

1. Ve a GitHub → Settings → SSH and GPG keys
2. Click en **"New SSH key"**
3. Pega tu clave pública
4. Click en **"Add SSH key"**

### 5. Cambiar remote a SSH

```bash
git remote set-url origin git@github.com:tu-usuario/zoreza-corte-semanal.git
```

## 📝 Buenas Prácticas

### Mensajes de Commit

Usa mensajes claros y descriptivos:

```bash
# ✅ Buenos ejemplos
git commit -m "feat: Agregar módulo de gastos para ADMIN"
git commit -m "fix: Corregir error de NoneType en navegación"
git commit -m "docs: Actualizar README con instrucciones de deployment"
git commit -m "style: Mejorar diseño de botones del dashboard"

# ❌ Malos ejemplos
git commit -m "cambios"
git commit -m "fix"
git commit -m "update"
```

### Prefijos Comunes

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato/estilo
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

### Commits Frecuentes

Haz commits pequeños y frecuentes en lugar de uno grande:

```bash
# Después de cada funcionalidad o fix
git add .
git commit -m "feat: Implementar búsqueda avanzada en historial"
git push
```

## 🌿 Workflow con Ramas

### Feature Branch

```bash
# Crear rama para nueva funcionalidad
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commits
git add .
git commit -m "feat: Implementar nueva funcionalidad"

# Subir rama
git push -u origin feature/nueva-funcionalidad

# Crear Pull Request en GitHub
# Después de aprobar, fusionar a main
git checkout main
git pull
git merge feature/nueva-funcionalidad
git push

# Eliminar rama local
git branch -d feature/nueva-funcionalidad

# Eliminar rama remota
git push origin --delete feature/nueva-funcionalidad
```

## 🔄 Mantener el Repositorio Actualizado

### Sincronizar con cambios remotos

```bash
# Antes de empezar a trabajar
git pull origin main

# Después de terminar
git push origin main
```

### Resolver conflictos

Si hay conflictos al hacer pull:

```bash
# Git marcará los archivos con conflictos
git status

# Edita los archivos manualmente
# Busca las marcas: <<<<<<< HEAD, =======, >>>>>>>

# Después de resolver
git add archivo-resuelto.py
git commit -m "fix: Resolver conflictos de merge"
git push
```

## 📊 GitHub Actions (CI/CD)

Para automatizar tests y deployment, crea `.github/workflows/main.yml`:

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -e .
    - name: Run tests
      run: |
        python -m pytest
```

## 🎯 Checklist Final

Antes de hacer tu primer push, verifica:

- [ ] `.gitignore` está configurado correctamente
- [ ] No hay archivos sensibles (contraseñas, tokens, etc.)
- [ ] `README.md` está actualizado
- [ ] `requirements.txt` tiene todas las dependencias
- [ ] El código funciona localmente
- [ ] Has hecho commit de todos los cambios importantes
- [ ] Los mensajes de commit son descriptivos

## 🆘 Problemas Comunes

### Error: "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/tu-usuario/zoreza-corte-semanal.git
```

### Error: "failed to push some refs"

```bash
# Primero descarga los cambios remotos
git pull origin main --rebase
git push origin main
```

### Error: "Permission denied (publickey)"

- Verifica que tu clave SSH esté configurada correctamente
- O usa HTTPS en lugar de SSH

### Archivo grande rechazado

```bash
# Si accidentalmente agregaste un archivo grande
git rm --cached archivo-grande.db
echo "archivo-grande.db" >> .gitignore
git commit -m "fix: Remover archivo grande del repositorio"
git push
```

## 📚 Recursos Adicionales

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

**¡Listo para subir tu código! 🚀**