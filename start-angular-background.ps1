# Iniciar Angular en segundo plano
Write-Host "Iniciando Angular en segundo plano..." -ForegroundColor Cyan

$env:Path = "C:\Program Files\nodejs;$env:Path"
cd frontend

# Iniciar proceso en segundo plano
$process = Start-Process -FilePath "node" `
    -ArgumentList "`"$PSScriptRoot\frontend\node_modules\@angular\cli\bin\ng`" serve --proxy-config proxy.conf.json --port 4200" `
    -WorkingDirectory "$PSScriptRoot\frontend" `
    -PassThru -NoNewWindow

$pid = $process.Id
Write-Host "Angular iniciado con PID: $pid" -ForegroundColor Green
Write-Host "Frontend URL: http://localhost:4200/" -ForegroundColor Green
Write-Host "Para detener: taskkill /PID $pid /F" -ForegroundColor Yellow

# Guardar PID en archivo para referencia
$pid | Out-File "$PSScriptRoot\angular.pid" -Encoding ASCII

# Esperar unos segundos para que se inicie
Start-Sleep -Seconds 10

# Probar conexión
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4200/" -TimeoutSec 5 -ErrorAction Stop -UseBasicParsing
    Write-Host "Frontend responde: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Advertencia: No se pudo conectar al frontend: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Backend Django: http://localhost:8000/api/turnos/" -ForegroundColor Cyan
Write-Host "Frontend Angular: http://localhost:4200/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Sistema completo iniciado!" -ForegroundColor Green