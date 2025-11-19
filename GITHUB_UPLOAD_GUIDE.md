# 📤 Guía de Subida a GitHub

## Opción 1: PowerShell (Windows) - RECOMENDADO

```powershell
# Ejecutar el script
.\upload_to_github.ps1 -GitHubUser "TU_USUARIO"

# Ejemplo:
.\upload_to_github.ps1 -GitHubUser "Bassi"
```

## Opción 2: Bash (Linux/Mac/Git Bash en Windows)

```bash
# Dar permisos de ejecución
chmod +x upload_to_github.sh

# Ejecutar el script
./upload_to_github.sh TU_USUARIO

# Ejemplo:
./upload_to_github.sh Bassi
```

## Opción 3: Manual (Paso a Paso)

### 1. Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `adnd-2e-dm-assistant`
3. Descripción: `Complete AD&D 2nd Edition Dungeon Master Assistant`
4. ❌ **NO marcar** "Initialize this repository with a README"
5. Click "Create repository"

### 2. Ejecutar comandos

```powershell
# Ir al directorio
cd "c:\Users\Bassi\proyects\Partidas en solitario\AD&D\progrmas"

# Limpiar cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Inicializar Git
git init

# Configurar usuario (si es primera vez)
git config user.name "Tu Nombre"
git config user.email "tu@email.com"

# Agregar archivos
git add .

# Hacer commit
git commit -m "Initial commit: Complete AD&D 2e DM Assistant system"

# Conectar con GitHub (reemplaza TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/adnd-2e-dm-assistant.git

# Renombrar branch
git branch -M main

# Subir
git push -u origin main
```

## 🔑 Autenticación

GitHub ya no acepta passwords. Necesitas usar:

### Opción A: Personal Access Token (PAT)

1. Ve a https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Selecciona scopes: `repo` (todos)
4. Copia el token generado
5. Cuando git pida password, usa el **token** en lugar de tu password

### Opción B: SSH Keys

```powershell
# Generar SSH key
ssh-keygen -t ed25519 -C "tu@email.com"

# Copiar la clave pública
Get-Content ~\.ssh\id_ed25519.pub | Set-Clipboard

# Agregar en GitHub:
# https://github.com/settings/keys
# Click "New SSH key"
# Pega la clave

# Usar URL SSH en vez de HTTPS
git remote set-url origin git@github.com:TU_USUARIO/adnd-2e-dm-assistant.git
```

## 📋 Checklist Pre-Subida

- [ ] Repositorio creado en GitHub
- [ ] Git instalado localmente
- [ ] Credenciales configuradas (PAT o SSH)
- [ ] Cache de Python limpiado
- [ ] .gitignore configurado
- [ ] README.md completo

## ❓ Solución de Problemas

### "fatal: repository not found"
→ El repositorio no existe en GitHub. Créalo primero.

### "Authentication failed"
→ Usa un Personal Access Token en vez de tu password.

### "Permission denied (publickey)"
→ Configura tus SSH keys correctamente.

### "refusing to merge unrelated histories"
→ Si creaste el repo con README, usa:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 🎯 Después de Subir

1. **Agrega Topics/Tags:**
   - python
   - dnd
   - dungeons-and-dragons
   - ad-d
   - rpg
   - game-master
   - tabletop-rpg

2. **Agrega una Licencia:**
   - Settings → Add a license
   - Recomendado: MIT o GPL-3.0

3. **Configura GitHub Pages (opcional):**
   - Para documentación online
   - Settings → Pages

4. **Agrega badges al README:**
   ```markdown
   ![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
   ![License](https://img.shields.io/badge/license-MIT-green.svg)
   ```

## 🔄 Actualizaciones Futuras

```bash
# Hacer cambios en el código
# ...

# Guardar cambios
git add .
git commit -m "Descripción de los cambios"
git push

# ¡Listo!
```

---

**¿Dudas?** Los scripts automáticos incluyen mensajes de ayuda detallados.
