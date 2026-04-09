# Script corregido para iniciar backend Django
# Corrige problemas: $pid reservado, -UseBasicParsing faltante, lógica mejorada

$ErrorActionPreference = "Stop"

Write-Host "=== INICIANDO BACKEND PANADERIA ==="
Write-Host "Fecha: $(Get-Date -Format 'HH:mm:ss')"
Write-Host ""

# Configurar rutas
$backendDir = Join-Path $PSScriptRoot "backend"
$python = Join-Path $backendDir "venv\Scripts\python.exe"
$manage = Join-Path $backendDir "manage.py"

# Verificar que existen los archivos necesarios
if (-not (Test-Path $python)) {
    Write-Host "ERROR: No se encuentra Python en $python" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $manage)) {
    Write-Host "ERROR: No se encuentra manage.py en $manage" -ForegroundColor Red
    exit 1
}

# Verificar si puerto 8000 está en uso
Write-Host "Verificando puerto 8000..."
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "ERROR: Puerto 8000 ya está en uso por PID: $($portInUse.OwningProcess)" -ForegroundColor Red
    Write-Host "Por favor detenga ese proceso y vuelva a intentar." -ForegroundColor Yellow
    exit 1
}

# Iniciar servidor Django
Write-Host "Iniciando servidor Django..."
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = $python
$processInfo.Arguments = "`"$manage`" runserver"
$processInfo.WorkingDirectory = $backendDir
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $false

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo
$process.Start() | Out-Null

$serverProcessId = $process.Id
Write-Host "Servidor iniciado con PID: $serverProcessId"

# Esperar a que el servidor se inicie
Write-Host "Esperando a que el servidor se inicialice..."
Start-Sleep -Seconds 10

# Probar la API
Write-Host "Probando conexion a la API..."
$apiTested = $false
$maxRetries = 5
$retryDelay = 3

for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        Write-Host "Intento $i de $maxRetries..."
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/turnos/" -TimeoutSec 5 -ErrorAction Stop -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "SUCCESS: API responde correctamente (HTTP 200)" -ForegroundColor Green
            $apiTested = $true
            break
        }
    } catch {
        Write-Host "Intento $i fallo: $($_.Exception.Message)" -ForegroundColor Yellow
        if ($i -lt $maxRetries) {
            Write-Host "Reintentando en $retryDelay segundos..." -ForegroundColor Gray
            Start-Sleep -Seconds $retryDelay
        }
    }
}

if (-not $apiTested) {
    Write-Host "ADVERTENCIA: No se pudo conectar a la API despues de $maxRetries intentos" -ForegroundColor Yellow
    Write-Host "El servidor puede estar iniciandose mas lento de lo esperado." -ForegroundColor Yellow
}

# Mostrar información del servidor
Write-Host ""
Write-Host "=== SERVIDOR BACKEND INICIADO ===" -ForegroundColor Green
Write-Host "PID: $serverProcessId" -ForegroundColor Cyan
Write-Host "URL: http://localhost:8000/" -ForegroundColor Cyan
Write-Host ""
Write-Host "ENDPOINTS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "  • API Root: http://localhost:8000/api/" -ForegroundColor White
Write-Host "  • Turnos: http://localhost:8000/api/turnos/" -ForegroundColor White
Write-Host "  • Clientes: http://localhost:8000/api/clientes/" -ForegroundColor White
Write-Host "  • Productos: http://localhost:8000/api/productos/" -ForegroundColor White
Write-Host "  • Admin: http://localhost:8000/admin/" -ForegroundColor White
Write-Host "  • JWT Token: http://localhost:8000/api/token/" -ForegroundColor White
Write-Host ""
Write-Host "CREDENCIALES DEMO:" -ForegroundColor Cyan
Write-Host "  Usuario: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "PARA DETENER EL SERVIDOR:" -ForegroundColor Yellow
Write-Host "  1. Presione Ctrl+C en esta ventana" -ForegroundColor White
Write-Host "  2. O ejecute: taskkill /PID $serverProcessId /F" -ForegroundColor White
Write-Host ""

# Mantener el proceso activo y mostrar logs
Write-Host "=== LOGS DEL SERVIDOR (Ctrl+C para detener) ===" -ForegroundColor Cyan
try {
    # Mostrar salida en tiempo real
    while (-not $process.HasExited) {
        if ($process.StandardOutput.Peek() -gt 0) {
            $output = $process.StandardOutput.ReadLine()
            Write-Host "[DJANGO] $output" -ForegroundColor Gray
        }
        Start-Sleep -Milliseconds 100
    }
} catch {
    # Capturar Ctrl+C u otros errores
    Write-Host ""
    Write-Host "Deteniendo servidor..." -ForegroundColor Yellow
} finally {
    # Asegurarse de que el proceso termine
    if (-not $process.HasExited) {
        $process.Kill()
        Start-Sleep -Seconds 2
    }
    Write-Host "Servidor detenido." -ForegroundColor Green
}