# Test rápido del backend - inicia, prueba y detiene
Write-Host "=== TEST RAPIDO BACKEND PANADERIA ==="

# Configurar rutas
$backendDir = Join-Path $PSScriptRoot "backend"
$python = Join-Path $backendDir "venv\Scripts\python.exe"
$manage = Join-Path $backendDir "manage.py"

# Verificar archivos
if (-not (Test-Path $python)) { Write-Host "ERROR: Python no encontrado"; exit 1 }
if (-not (Test-Path $manage)) { Write-Host "ERROR: manage.py no encontrado"; exit 1 }

# Limpiar puerto 8000
Write-Host "Limpieando puerto 8000..."
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "  Deteniendo proceso $($_.OwningProcess) en puerto 8000"
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# Iniciar servidor en segundo plano
Write-Host "Iniciando servidor Django..."
$process = Start-Process -FilePath $python -ArgumentList "`"$manage`" runserver" -WorkingDirectory $backendDir -PassThru -NoNewWindow
$serverPid = $process.Id
Write-Host "Servidor PID: $serverPid"

# Esperar inicio
Write-Host "Esperando inicializacion (10s)..."
Start-Sleep -Seconds 10

# Probar endpoints
$endpoints = @(
    "http://localhost:8000/api/turnos/",
    "http://localhost:8000/api/clientes/",
    "http://localhost:8000/api/productos/"
)

$allPassed = $true
foreach ($url in $endpoints) {
    try {
        Write-Host "Probando $url ..." -NoNewline
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop -UseBasicParsing
        Write-Host " OK (HTTP $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host " FALLIDO: $($_.Exception.Message)" -ForegroundColor Red
        $allPassed = $false
    }
}

# Probar admin (debería redirigir a login)
try {
    Write-Host "Probando admin (debe redirigir a login)..." -NoNewline
    $response = Invoke-WebRequest -Uri "http://localhost:8000/admin/" -TimeoutSec 5 -ErrorAction Stop -UseBasicParsing
    Write-Host " OK (HTTP $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host " FALLIDO: $($_.Exception.Message)" -ForegroundColor Red
    $allPassed = $false
}

# Detener servidor
Write-Host "Deteniendo servidor PID $serverPid..."
Stop-Process -Id $serverPid -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Verificar que se detuvo
$stillRunning = Get-Process -Id $serverPid -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Host "ADVERTENCIA: Proceso aún ejecutandose, forzando..." -ForegroundColor Yellow
    taskkill /F /PID $serverPid 2>$null
}

Write-Host ""
if ($allPassed) {
    Write-Host "=== TEST COMPLETADO EXITOSAMENTE ===" -ForegroundColor Green
    Write-Host "Backend Django funciona correctamente" -ForegroundColor Green
    Write-Host "Puede iniciar con: cd backend && venv\Scripts\activate.bat && python manage.py runserver" -ForegroundColor Cyan
} else {
    Write-Host "=== TEST CON FALLOS ===" -ForegroundColor Red
    Write-Host "Algunos endpoints no respondieron" -ForegroundColor Red
}