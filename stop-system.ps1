# Script para detener sistema Panadería completo
Write-Host "=== DETENIENDO SISTEMA PANADERÍA ==="
Write-Host ""

# 1. Detener Angular Frontend
Write-Host "1. Deteniendo Angular Frontend..." -ForegroundColor Cyan
$angularPidPath = Join-Path $PSScriptRoot "angular.pid"
if (Test-Path $angularPidPath) {
    $angularPid = Get-Content $angularPidPath -Raw
    Write-Host "   PID Angular: $angularPid"
    Stop-Process -Id $angularPid -Force -ErrorAction SilentlyContinue
    Remove-Item $angularPidPath -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Angular detenido" -ForegroundColor Green
} else {
    Write-Host "   ℹ No se encontró archivo PID de Angular" -ForegroundColor Yellow
    # Intentar encontrar procesos Node en puerto 4200
    $port4200 = Get-NetTCPConnection -LocalPort 4200 -ErrorAction SilentlyContinue
    if ($port4200) {
        Write-Host "   Deteniendo proceso en puerto 4200 (PID: $($port4200.OwningProcess))"
        Stop-Process -Id $port4200.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

# 2. Detener Django Backend
Write-Host "2. Deteniendo Django Backend..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "   PID Django: $($port8000.OwningProcess)"
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Django detenido" -ForegroundColor Green
} else {
    Write-Host "   ℹ No hay procesos en puerto 8000" -ForegroundColor Yellow
}

# 3. Verificar que los puertos están libres
Write-Host "3. Verificando puertos..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

$port4200Check = Get-NetTCPConnection -LocalPort 4200 -ErrorAction SilentlyContinue
$port8000Check = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if (-not $port4200Check -and -not $port8000Check) {
    Write-Host "   ✓ Puertos 4200 y 8000 liberados" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Algunos puertos aún en uso:" -ForegroundColor Yellow
    if ($port4200Check) { Write-Host "     • Puerto 4200: PID $($port4200Check.OwningProcess)" }
    if ($port8000Check) { Write-Host "     • Puerto 8000: PID $($port8000Check.OwningProcess)" }
    
    # Forzar detención si es necesario
    Write-Host "   Forzando detención de procesos restantes..." -ForegroundColor Yellow
    if ($port4200Check) { Stop-Process -Id $port4200Check.OwningProcess -Force -ErrorAction SilentlyContinue }
    if ($port8000Check) { Stop-Process -Id $port8000Check.OwningProcess -Force -ErrorAction SilentlyContinue }
}

Write-Host ""
Write-Host "=== SISTEMA DETENIDO ===" -ForegroundColor Green
Write-Host ""
Write-Host "Para reiniciar el sistema:" -ForegroundColor Cyan
Write-Host "  1. Backend: Ejecute 'test-backend-quick.ps1' o inicie manualmente:" -ForegroundColor White
Write-Host "     cd backend && venv\Scripts\activate.bat && python manage.py runserver" -ForegroundColor Gray
Write-Host "  2. Frontend: Ejecute 'start-angular-background.ps1'" -ForegroundColor White
Write-Host ""
Write-Host "O pruebe el sistema completo con:" -ForegroundColor Cyan
Write-Host "  1. Verifique backend: http://localhost:8000/api/turnos/" -ForegroundColor White
Write-Host "  2. Acceda frontend: http://localhost:4200/" -ForegroundColor White
Write-Host "  3. Admin Django: http://localhost:8000/admin/" -ForegroundColor White