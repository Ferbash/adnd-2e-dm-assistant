#!/bin/bash
# Script para subir el proyecto AD&D 2e a GitHub
# Uso: ./upload_to_github.sh TU_USUARIO

set -e  # Detener si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar argumento
if [ -z "$1" ]; then
    echo -e "${RED}Error: Debes proporcionar tu usuario de GitHub${NC}"
    echo "Uso: ./upload_to_github.sh TU_USUARIO"
    echo "Ejemplo: ./upload_to_github.sh Bassi"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME="adnd-2e-dm-assistant"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo -e "${GREEN}🎲 Subiendo AD&D 2e DM Assistant a GitHub${NC}"
echo "=========================================="
echo ""

# Verificar si Git está instalado
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git no está instalado. Por favor instala Git primero.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Paso 1: Limpiando archivos temporales...${NC}"
# Limpiar cache de Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Cache limpiado${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 2: Inicializando Git...${NC}"
if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}✅ Repositorio Git inicializado${NC}"
else
    echo -e "${GREEN}✅ Git ya inicializado${NC}"
fi
echo ""

echo -e "${YELLOW}📋 Paso 3: Configurando usuario Git (si es necesario)...${NC}"
if [ -z "$(git config user.name)" ]; then
    read -p "Ingresa tu nombre para Git: " git_name
    git config user.name "$git_name"
fi
if [ -z "$(git config user.email)" ]; then
    read -p "Ingresa tu email para Git: " git_email
    git config user.email "$git_email"
fi
echo -e "${GREEN}✅ Usuario: $(git config user.name) <$(git config user.email)>${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 4: Agregando archivos...${NC}"
git add .
echo -e "${GREEN}✅ Archivos agregados${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 5: Creando commit...${NC}"
git commit -m "Initial commit: Complete AD&D 2e DM Assistant system

Features:
- Character creator with 6 races and 6 classes
- Combat system with 94 monsters
- Rules database with intelligent search (biblio.py)
- Multiple interfaces (console, GUI, party manager)
- Dice roller with THAC0 system
- Distance-based combat mechanics
- Auto-combat mode
- 25+ spells database

Technical:
- Organized modular structure (core/, interfaces/, utils/)
- Python 3.7+ compatible
- No external dependencies required
- UTF-8 encoding support for Windows
- Comprehensive documentation" || echo -e "${YELLOW}⚠️ Sin cambios para commit o ya hay un commit${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 6: Configurando remote...${NC}"
if git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}Remote 'origin' ya existe. Actualizando...${NC}"
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi
echo -e "${GREEN}✅ Remote configurado: ${REPO_URL}${NC}"
echo ""

echo -e "${YELLOW}📋 Paso 7: Renombrando branch a 'main'...${NC}"
git branch -M main
echo -e "${GREEN}✅ Branch renombrado${NC}"
echo ""

echo -e "${GREEN}=========================================="
echo "🎲 Listo para subir a GitHub!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️ IMPORTANTE: Antes de continuar, asegúrate de:${NC}"
echo "   1. Haber creado el repositorio en GitHub:"
echo "      https://github.com/new"
echo "      Nombre: ${REPO_NAME}"
echo "      ❌ NO marcar 'Initialize with README'"
echo ""
echo "   2. Si el repositorio es privado, necesitarás:"
echo "      - Token de acceso personal (PAT), o"
echo "      - SSH keys configuradas"
echo ""
read -p "¿Continuar con el push? (s/n): " confirm

if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    echo -e "${YELLOW}❌ Push cancelado${NC}"
    echo ""
    echo "Cuando estés listo, ejecuta:"
    echo "  git push -u origin main"
    exit 0
fi

echo ""
echo -e "${YELLOW}📋 Paso 8: Subiendo a GitHub...${NC}"
echo -e "${YELLOW}(Te pedirá usuario y password/token de GitHub)${NC}"
echo ""

if git push -u origin main; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ ¡Proyecto subido exitosamente!"
    echo "==========================================${NC}"
    echo ""
    echo "🔗 Tu repositorio está en:"
    echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"
    echo ""
    echo "📝 Próximos pasos:"
    echo "   1. Visita tu repositorio en GitHub"
    echo "   2. Agrega temas/tags: python, dnd, ad&d, rpg, game-master"
    echo "   3. Considera agregar una licencia"
    echo "   4. ¡Comparte tu proyecto!"
else
    echo ""
    echo -e "${RED}=========================================="
    echo "❌ Error al subir a GitHub"
    echo "==========================================${NC}"
    echo ""
    echo "Posibles causas:"
    echo "  1. El repositorio no existe en GitHub"
    echo "  2. Credenciales incorrectas"
    echo "  3. Problemas de permisos"
    echo ""
    echo "Soluciones:"
    echo "  1. Verifica que creaste el repo: https://github.com/${GITHUB_USER}/${REPO_NAME}"
    echo "  2. Usa un Personal Access Token en vez de password"
    echo "  3. Configura SSH keys"
    echo ""
    echo "Para intentar de nuevo:"
    echo "  git push -u origin main"
    exit 1
fi
