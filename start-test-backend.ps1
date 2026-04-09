$backendDir = Join-Path $PSScriptRoot "backend"
$python = Join-Path $backendDir "venv\Scripts\python.exe"
$manage = Join-Path $backendDir "manage.py"

Write-Host "=== PANADERÍA BACKEND TEST ==="

# Check if port 8000 is already in use
Write-Host "Checking port 8000..."
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($portProcess) {
    Write-Host "ERROR: Port 8000 is already in use by process: $($portProcess.OwningProcess)"
    Write-Host "Please stop the process and try again."
    exit 1
}

Write-Host "Starting Django backend server..."
$process = Start-Process -FilePath $python -ArgumentList "`"$manage`" runserver" -WorkingDirectory $backendDir -NoNewWindow -PassThru
$serverPid = $process.Id
Write-Host "Server started with PID $serverPid"

# Wait for server to start
Write-Host "Waiting for server to initialize..."
Start-Sleep -Seconds 8

# Test API endpoint with retries
$maxRetries = 3
$success = $false
for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        Write-Host "Testing API (attempt $i/$maxRetries)..."
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/turnos/" -TimeoutSec 10 -ErrorAction Stop -UseBasicParsing
        Write-Host "Backend API is accessible via /api/turnos/. Status:" $response.StatusCode
        $success = $true
        break
    } catch {
        Write-Host "Attempt $i failed: $_"
        if ($i -lt $maxRetries) {
            Start-Sleep -Seconds 3
        }
    }
}

if (-not $success) {
    Write-Host "ERROR: Backend API is not responding after $maxRetries attempts."
}

# Stop the server
Stop-Process -Id $serverPid -Force -ErrorAction SilentlyContinue
Write-Host "Stopped backend server."