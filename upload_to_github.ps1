# Script PowerShell para subir el proyecto AD&D 2e a GitHub
# Uso: .\upload_to_github.ps1 -GitHubUser "TU_USUARIO"

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUser,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "adnd-2e-dm-assistant"
)

$ErrorActionPreference = "Stop"

# Colores
function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "Subiendo AD&D 2e DM Assistant a GitHub"
Write-Output "=========================================="
Write-Output ""

$RepoUrl = "https://github.com/$GitHubUser/$RepoName.git"

# Verificar Git
try {
    $null = Get-Command git -ErrorAction Stop
} catch {
    Write-ColorOutput Red "Git no esta instalado. Por favor instala Git primero."
    Write-Output "Descarga: https://git-scm.com/download/win"
    exit 1
}

Write-ColorOutput Yellow "Paso 1: Limpiando archivos temporales..."
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "*.pyo" | Remove-Item -Force -ErrorAction SilentlyContinue
Write-ColorOutput Green "Cache limpiado"
Write-Output ""

Write-ColorOutput Yellow "Paso 2: Inicializando Git..."
if (-not (Test-Path .git)) {
    git init
    Write-ColorOutput Green "Repositorio Git inicializado"
} else {
    Write-ColorOutput Green "Git ya inicializado"
}
Write-Output ""

Write-ColorOutput Yellow "Paso 3: Configurando usuario Git..."
$gitName = git config user.name
$gitEmail = git config user.email

if ([string]::IsNullOrEmpty($gitName)) {
    $gitName = Read-Host "Ingresa tu nombre para Git"
    git config user.name "$gitName"
}

if ([string]::IsNullOrEmpty($gitEmail)) {
    $gitEmail = Read-Host "Ingresa tu email para Git"
    git config user.email "$gitEmail"
}

Write-ColorOutput Green "Usuario configurado: $gitName"
Write-Output ""

Write-ColorOutput Yellow "Paso 4: Agregando archivos..."
git add .
Write-ColorOutput Green "Archivos agregados"
Write-Output ""

Write-ColorOutput Yellow "Paso 5: Creando commit..."
try {
    $commitMessage = "Initial commit: Complete AD&D 2e DM Assistant system`n`nFeatures:`n- Character creator with 6 races and 6 classes`n- Combat system with 94 monsters`n- Rules database with intelligent search`n- Multiple interfaces`n- Dice roller with THAC0 system"
    git commit -m $commitMessage
    Write-ColorOutput Green "Commit creado"
} catch {
    Write-ColorOutput Yellow "Sin cambios para commit o ya hay un commit"
}
Write-Output ""

Write-ColorOutput Yellow "Paso 6: Configurando remote..."
try {
    $currentRemote = git remote get-url origin 2>$null
    Write-ColorOutput Yellow "Remote 'origin' ya existe. Actualizando..."
    git remote set-url origin $RepoUrl
} catch {
    git remote add origin $RepoUrl
}
Write-ColorOutput Green "Remote configurado: $RepoUrl"
Write-Output ""

Write-ColorOutput Yellow "Paso 7: Renombrando branch a 'main'..."
git branch -M main
Write-ColorOutput Green "Branch renombrado"
Write-Output ""

Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "Listo para subir a GitHub!"
Write-ColorOutput Green "=========================================="
Write-Output ""
Write-ColorOutput Yellow "IMPORTANTE: Antes de continuar, asegurate de:"
Write-Output "   1. Haber creado el repositorio en GitHub:"
Write-Output "      https://github.com/new"
Write-Output "      Nombre: $RepoName"
Write-Output "      NO marcar 'Initialize with README'"
Write-Output ""
Write-Output "   2. Si el repositorio es privado, necesitarás:"
Write-Output "      - Token de acceso personal (PAT), o"
Write-Output "      - SSH keys configuradas"
Write-Output ""

$confirm = Read-Host "¿Continuar con el push? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-ColorOutput Yellow "Push cancelado"
    Write-Output ""
    Write-Output "Cuando estés listo, ejecuta:"
    Write-Output "  git push -u origin main"
    exit 0
}

Write-Output ""
Write-ColorOutput Yellow "Paso 8: Subiendo a GitHub..."
Write-ColorOutput Yellow "(Te pedira usuario y password/token de GitHub)"
Write-Output ""

try {
    git push -u origin main
    Write-Output ""
    Write-ColorOutput Green "=========================================="
    Write-ColorOutput Green "Proyecto subido exitosamente!"
    Write-ColorOutput Green "=========================================="
    Write-Output ""
    Write-Output "Tu repositorio esta en:"
    Write-Output "   https://github.com/$GitHubUser/$RepoName"
    Write-Output ""
    Write-Output "Proximos pasos:"
    Write-Output "   1. Visita tu repositorio en GitHub"
    Write-Output "   2. Agrega temas/tags: python, dnd, ad&d, rpg, game-master"
    Write-Output "   3. Considera agregar una licencia"
    Write-Output "   4. ¡Comparte tu proyecto!"
} catch {
    Write-Output ""
    Write-ColorOutput Red "=========================================="
    Write-ColorOutput Red "Error al subir a GitHub"
    Write-ColorOutput Red "=========================================="
    Write-Output ""
    Write-Output "Posibles causas:"
    Write-Output "  1. El repositorio no existe en GitHub"
    Write-Output "  2. Credenciales incorrectas"
    Write-Output "  3. Problemas de permisos"
    Write-Output ""
    Write-Output "Soluciones:"
    Write-Output "  1. Verifica que creaste el repo: https://github.com/$GitHubUser/$RepoName"
    Write-Output "  2. Usa un Personal Access Token en vez de password"
    Write-Output "     Crear token: https://github.com/settings/tokens"
    Write-Output "  3. Configura SSH keys"
    Write-Output ""
    Write-Output "Para intentar de nuevo:"
    Write-Output "  git push -u origin main"
    exit 1
}
