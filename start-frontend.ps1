# Script para iniciar frontend Angular con PATH corregido
Write-Host "=== INICIANDO FRONTEND ANGULAR ==="
Write-Host ""

# Agregar Node.js al PATH si no está
$nodePath = "C:\Program Files\nodejs"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Process")
if ($currentPath -notlike "*$nodePath*") {
    Write-Host "Agregando Node.js al PATH..." -ForegroundColor Yellow
    $newPath = "$nodePath;$currentPath"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Process")
    Write-Host "PATH actualizado" -ForegroundColor Green
}

# Verificar Node.js y npm
Write-Host "Verificando Node.js..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js no disponible en PATH" -ForegroundColor Red
    exit 1
}

Write-Host "Verificando npm..." -ForegroundColor Cyan
try {
    $npmVersion = npm --version
    Write-Host "npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: npm no disponible" -ForegroundColor Red
    exit 1
}

# Verificar que estamos en el directorio correcto
$frontendDir = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path $frontendDir)) {
    Write-Host "ERROR: Directorio frontend no encontrado" -ForegroundColor Red
    exit 1
}

Set-Location $frontendDir

# Verificar dependencias
Write-Host "Verificando dependencias Angular..." -ForegroundColor Cyan
if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias (puede tardar unos minutos)..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Falló la instalación de dependencias" -ForegroundColor Red
        exit 1
    }
}

# Verificar que Angular CLI esté disponible
Write-Host "Verificando Angular CLI..." -ForegroundColor Cyan
try {
    $ngVersion = npx ng version 2>&1 | Select-String "Angular CLI"
    if ($ngVersion) {
        Write-Host "Angular CLI disponible" -ForegroundColor Green
    } else {
        Write-Host "Instalando Angular CLI globalmente..." -ForegroundColor Yellow
        npm install -g @angular/cli
    }
} catch {
    Write-Host "ADVERTENCIA: No se pudo verificar Angular CLI" -ForegroundColor Yellow
}

# Iniciar servidor de desarrollo Angular con proxy
Write-Host ""
Write-Host "Iniciando servidor Angular..." -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:4200/" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000/api/" -ForegroundColor White
Write-Host "Proxy configurado: /api -> http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales demo:" -ForegroundColor Cyan
Write-Host "  Usuario: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Presione Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
npx ng serve --proxy-config proxy.conf.json --open