Write-Host "=== VERIFICACIÓN SISTEMA PANADERÍA ==="
Write-Host "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# 1. Verificar PostgreSQL
Write-Host "1. Verificando PostgreSQL..." -ForegroundColor Cyan
$postgresProcesses = tasklist | findstr postgres
if ($postgresProcesses) {
    Write-Host "   ✓ PostgreSQL está ejecutándose" -ForegroundColor Green
} else {
    Write-Host "   ✗ PostgreSQL NO está ejecutándose" -ForegroundColor Red
}

# 2. Verificar conexión a base de datos
Write-Host "2. Verificando conexión a base de datos 'panaderia_db'..." -ForegroundColor Cyan
$pythonPath = Join-Path $PSScriptRoot "backend\venv\Scripts\python.exe"
$managePath = Join-Path $PSScriptRoot "backend\manage.py"
if (Test-Path $pythonPath -and Test-Path $managePath) {
    try {
        $output = & $pythonPath $managePath check --database default 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Conexión a base de datos OK" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Error conexión DB: $output" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ✗ Error ejecutando verificación: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ✗ No se encontró Python o manage.py" -ForegroundColor Red
}

# 3. Verificar puerto 8000
Write-Host "3. Verificando puerto 8000..." -ForegroundColor Cyan
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portProcess) {
    Write-Host "   ⚠ Puerto 8000 en uso por PID: $($portProcess.OwningProcess)" -ForegroundColor Yellow
} else {
    Write-Host "   ✓ Puerto 8000 disponible" -ForegroundColor Green
}

# 4. Verificar Node.js y npm
Write-Host "4. Verificando Node.js..." -ForegroundColor Cyan
$nodePath = "C:\Program Files\nodejs\node.exe"
if (Test-Path $nodePath) {
    Write-Host "   ✓ Node.js instalado en: $nodePath" -ForegroundColor Green
    try {
        $nodeVersion = & $nodePath --version
        Write-Host "   ✓ Node versión: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠ No se pudo obtener versión de Node" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ Node.js NO instalado" -ForegroundColor Red
}

# Verificar npm en PATH
Write-Host "5. Verificando npm en PATH..." -ForegroundColor Cyan
try {
    $npmVersion = npm --version 2>$null
    if ($npmVersion) {
        Write-Host "   ✓ npm disponible en PATH: v$npmVersion" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ npm NO en PATH (pero Node instalado)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠ npm NO accesible desde PATH" -ForegroundColor Yellow
}

# 6. Verificar estructura de directorios
Write-Host "6. Verificando estructura de directorios..." -ForegroundColor Cyan
$requiredDirs = @(
    "backend",
    "backend\api",
    "backend\panaderia_backend", 
    "frontend",
    "frontend\src",
    "frontend\src\app"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (Test-Path $fullPath) {
        Write-Host "   ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $dir (FALTA)" -ForegroundColor Red
    }
}

# 7. Verificar archivos críticos
Write-Host "7. Verificando archivos críticos..." -ForegroundColor Cyan
$criticalFiles = @(
    "backend\manage.py",
    "backend\.env",
    "backend\requirements.txt",
    "backend\panaderia_backend\settings.py",
    "backend\panaderia_backend\urls.py",
    "backend\api\models.py",
    "backend\api\views.py",
    "frontend\package.json",
    "frontend\angular.json"
)

foreach ($file in $criticalFiles) {
    $fullPath = Join-Path $PSScriptRoot $file
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "   ✓ $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file (FALTA)" -ForegroundColor Red
    }
}

# 8. Verificar migraciones Django
Write-Host "8. Verificando migraciones Django..." -ForegroundColor Cyan
if (Test-Path $pythonPath -and Test-Path $managePath) {
    try {
        $migrations = & $pythonPath $managePath showmigrations --list 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Migraciones disponibles" -ForegroundColor Green
            # Contar migraciones aplicadas
            $applied = ($migrations | Select-String "\[X\]").Count
            $total = ($migrations | Select-String "\[.\]").Count
            Write-Host "     Aplicadas: $applied/$total" -ForegroundColor Cyan
        } else {
            Write-Host "   ✗ Error verificando migraciones" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ✗ Error: $_" -ForegroundColor Red
    }
}

# 9. Verificar entorno virtual Python
Write-Host "9. Verificando entorno virtual Python..." -ForegroundColor Cyan
$venvPython = Join-Path $PSScriptRoot "backend\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "   ✓ Entorno virtual encontrado" -ForegroundColor Green
    try {
        $pythonVersion = & $venvPython --version
        Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠ No se pudo obtener versión Python" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ NO hay entorno virtual Python" -ForegroundColor Red
}

# 10. Resumen
Write-Host ""
Write-Host "=== RESUMEN ===" -ForegroundColor Cyan
Write-Host "Para iniciar sistema manualmente:"
Write-Host "  1. BACKEND: cd backend && venv\Scripts\activate.bat && python manage.py runserver"
Write-Host "  2. FRONTEND: cd frontend && npm start"
Write-Host ""
Write-Host "Para probar backend (puerto 8000):"
Write-Host "  curl http://localhost:8000/api/turnos/"
Write-Host "  curl http://localhost:8000/admin/"
Write-Host ""
Write-Host "Para probar frontend (puerto 4200):"
Write-Host "  Navegar a http://localhost:4200/"
Write-Host ""

# Recomendaciones
$issues = @()
if (-not $postgresProcesses) { $issues += "PostgreSQL no está ejecutándose" }
if ($portProcess) { $issues += "Puerto 8000 en uso" }
if (-not (Test-Path $nodePath)) { $issues += "Node.js no instalado" }
if (-not (Test-Path $venvPython)) { $issues += "No hay entorno virtual Python" }

if ($issues.Count -gt 0) {
    Write-Host "⚠ PROBLEMAS DETECTADOS:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  • $issue" -ForegroundColor Red
    }
} else {
    Write-Host "✓ Sistema listo para ejecutar" -ForegroundColor Green
}