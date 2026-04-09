Write-Host "=== VERIFICACIÓN SISTEMA PANADERÍA ==="
Write-Host "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# 1. Verificar PostgreSQL
Write-Host "1. Verificando PostgreSQL..." -ForegroundColor Cyan
try {
    $postgresProcesses = tasklist.exe | findstr.exe postgres 2>$null
    if ($postgresProcesses) {
        Write-Host "   OK: PostgreSQL está ejecutándose" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: PostgreSQL NO está ejecutándose" -ForegroundColor Red
    }
} catch {
    Write-Host "   ERROR: No se pudo verificar PostgreSQL" -ForegroundColor Red
}

# 2. Verificar puerto 8000
Write-Host "2. Verificando puerto 8000..." -ForegroundColor Cyan
try {
    $portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($portProcess) {
        Write-Host "   ADVERTENCIA: Puerto 8000 en uso por PID: $($portProcess.OwningProcess)" -ForegroundColor Yellow
    } else {
        Write-Host "   OK: Puerto 8000 disponible" -ForegroundColor Green
    }
} catch {
    Write-Host "   ERROR: No se pudo verificar puerto 8000" -ForegroundColor Red
}

# 3. Verificar Node.js
Write-Host "3. Verificando Node.js..." -ForegroundColor Cyan
$nodePath = "C:\Program Files\nodejs\node.exe"
if (Test-Path $nodePath) {
    Write-Host "   OK: Node.js instalado en: $nodePath" -ForegroundColor Green
    try {
        $nodeVersion = & $nodePath --version
        Write-Host "   OK: Node versión: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ADVERTENCIA: No se pudo obtener versión de Node" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ERROR: Node.js NO instalado" -ForegroundColor Red
}

# 4. Verificar npm
Write-Host "4. Verificando npm..." -ForegroundColor Cyan
try {
    # Intentar con PATH completo primero
    $npmPath = "C:\Program Files\nodejs\npm.cmd"
    if (Test-Path $npmPath) {
        $npmVersion = & $npmPath --version 2>$null
        Write-Host "   OK: npm disponible (v$npmVersion)" -ForegroundColor Green
    } else {
        Write-Host "   ADVERTENCIA: npm.cmd no encontrado en ruta esperada" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ADVERTENCIA: npm NO accesible" -ForegroundColor Yellow
}

# 5. Verificar Python y entorno virtual
Write-Host "5. Verificando Python y entorno virtual..." -ForegroundColor Cyan
$venvPython = Join-Path $PSScriptRoot "backend\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "   OK: Entorno virtual Python encontrado" -ForegroundColor Green
    try {
        $pythonVersion = & $venvPython --version
        Write-Host "   OK: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ERROR: No se pudo obtener versión Python" -ForegroundColor Red
    }
} else {
    Write-Host "   ERROR: NO hay entorno virtual Python" -ForegroundColor Red
}

# 6. Verificar Django
Write-Host "6. Verificando Django..." -ForegroundColor Cyan
if (Test-Path $venvPython) {
    $managePath = Join-Path $PSScriptRoot "backend\manage.py"
    if (Test-Path $managePath) {
        Write-Host "   OK: manage.py encontrado" -ForegroundColor Green
        
        try {
            # Verificar si Django puede importarse
            $checkOutput = & $venvPython $managePath check 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   OK: Django project check passed" -ForegroundColor Green
            } else {
                Write-Host "   ERROR: Django project check failed:" -ForegroundColor Red
                Write-Host "   $checkOutput" -ForegroundColor Red
            }
        } catch {
            Write-Host "   ERROR: No se pudo ejecutar Django check: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "   ERROR: manage.py no encontrado" -ForegroundColor Red
    }
}

# 7. Verificar migraciones
Write-Host "7. Verificando migraciones Django..." -ForegroundColor Cyan
if (Test-Path $venvPython -and Test-Path $managePath) {
    try {
        $migrations = & $venvPython $managePath showmigrations 2>&1
        if ($LASTEXITCODE -eq 0) {
            $appliedCount = 0
            $totalCount = 0
            foreach ($line in $migrations) {
                if ($line -match '\[X\]') { $appliedCount++ }
                if ($line -match '\[.\]') { $totalCount++ }
            }
            Write-Host "   OK: Migraciones disponibles" -ForegroundColor Green
            Write-Host "       Aplicadas: $appliedCount de $totalCount" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "   ERROR: No se pudo verificar migraciones" -ForegroundColor Red
    }
}

# 8. Verificar Angular
Write-Host "8. Verificando Angular..." -ForegroundColor Cyan
$packageJson = Join-Path $PSScriptRoot "frontend\package.json"
$angularJson = Join-Path $PSScriptRoot "frontend\angular.json"
if (Test-Path $packageJson -and Test-Path $angularJson) {
    Write-Host "   OK: Proyecto Angular encontrado" -ForegroundColor Green
    
    # Verificar node_modules
    $nodeModules = Join-Path $PSScriptRoot "frontend\node_modules"
    if (Test-Path $nodeModules) {
        $dirCount = (Get-ChildItem $nodeModules -Directory | Measure-Object).Count
        Write-Host "   OK: node_modules instalado ($dirCount paquetes)" -ForegroundColor Green
    } else {
        Write-Host "   ADVERTENCIA: node_modules no instalado" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ERROR: Proyecto Angular incompleto" -ForegroundColor Red
}

# Resumen y recomendaciones
Write-Host ""
Write-Host "=== RESUMEN Y RECOMENDACIONES ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para probar manualmente:"
Write-Host "  1. BACKEND: cd backend && venv\Scripts\activate.bat && python manage.py runserver"
Write-Host "  2. Verificar en navegador: http://localhost:8000/api/turnos/"
Write-Host "  3. FRONTEND: cd frontend && npm start"
Write-Host "  4. Verificar en navegador: http://localhost:4200/"
Write-Host ""
Write-Host "Comandos de diagnóstico:"
Write-Host "  - Probar API: curl http://localhost:8000/api/turnos/"
Write-Host "  - Admin Django: http://localhost:8000/admin/"
Write-Host "  - Usuario demo: admin / admin123"
Write-Host ""

# Verificar si hay problemas críticos
$criticalIssues = @()

if (-not (Test-Path $venvPython)) {
    $criticalIssues += "Falta entorno virtual Python en backend\venv\"
}

if (-not (Test-Path "C:\Program Files\nodejs\node.exe")) {
    $criticalIssues += "Node.js no instalado o no en ruta esperada"
}

if ($criticalIssues.Count -gt 0) {
    Write-Host "PROBLEMAS CRÍTICOS:" -ForegroundColor Red
    foreach ($issue in $criticalIssues) {
        Write-Host "  • $issue" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "SOLUCIONES:"
    Write-Host "  1. Para Python: cd backend && python -m venv venv"
    Write-Host "  2. Para Node.js: Descargar desde nodejs.org (LTS v24.14.1)"
} else {
    Write-Host "SISTEMA LISTO para ejecutar" -ForegroundColor Green
}