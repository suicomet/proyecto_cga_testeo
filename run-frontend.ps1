# Script para ejecutar frontend Angular
Write-Host "=== EJECUTANDO FRONTEND ANGULAR ==="
Write-Host ""

# Configurar PATH
$env:Path = "C:\Program Files\nodejs;$env:Path"

# Verificar Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js no disponible" -ForegroundColor Red
    exit 1
}

cd frontend

Write-Host "Iniciando servidor Angular en http://localhost:4200/" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000/api/" -ForegroundColor White
Write-Host "Proxy configurado: /api -> http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales demo:" -ForegroundColor Cyan
Write-Host "  Usuario: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Presione Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
npx ng serve --proxy-config proxy.conf.json