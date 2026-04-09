$backendDir = "E:\panaderia_proyecto\backend"
$python = Join-Path $backendDir "venv\Scripts\python.exe"
$manage = Join-Path $backendDir "manage.py"

Write-Host "=== PANADERÍA BACKEND STARTUP ==="

# Check if port 8000 is already in use
Write-Host "Checking port 8000..."
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($portProcess) {
    Write-Host "ERROR: Port 8000 is already in use by process: $($portProcess.OwningProcess)"
    Write-Host "Please stop the process or use a different port."
    exit 1
}

# Verify PostgreSQL connection
Write-Host "Verifying PostgreSQL connection..."
try {
    $env:PGPASSWORD='postgres'
    $psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
    if (Test-Path $psql) {
        & $psql -h localhost -p 5432 -U postgres -d panaderia_db -c "SELECT 1" -q -t > $null
        Write-Host "PostgreSQL connection: OK"
    } else {
        Write-Host "WARNING: PostgreSQL client not found at $psql"
        Write-Host "PostgreSQL connection check skipped."
    }
} catch {
    Write-Host "WARNING: PostgreSQL connection check failed: $_"
    Write-Host "Continuing anyway, but database issues may occur."
}

Write-Host "Starting Django backend server..."
# Start server process
$process = Start-Process -FilePath $python -ArgumentList "`"$manage`" runserver" -WorkingDirectory $backendDir -PassThru -NoNewWindow
$serverPid = $process.Id
Write-Host "Server process started with PID: $serverPid"

# Wait for server to initialize
Write-Host "Waiting for server to start..."
Start-Sleep -Seconds 3

# Test if server is responding with progressive wait
$maxRetries = 10
$success = $false
for ($i = 1; $i -le $maxRetries; $i++) {
    try {
        Write-Host "Testing API connection (attempt $i/$maxRetries)..."
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/turnos/" -TimeoutSec 5 -ErrorAction Stop -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $success = $true
            Write-Host "SUCCESS: Backend API is accessible via /api/turnos/. Status: $($response.StatusCode)"
            Write-Host "Server is running at http://localhost:8000/"
            Write-Host "API root: http://localhost:8000/api/"
            Write-Host "Admin: http://localhost:8000/admin/"
            Write-Host "Use Ctrl+C in this window to stop the server."
            break
        }
    } catch {
        Write-Host "Attempt $i failed: $($_.Exception.Message)"
        if ($i -lt $maxRetries) {
            $waitTime = 3
            Write-Host "Waiting $waitTime seconds before next attempt..."
            Start-Sleep -Seconds $waitTime
        }
    }
}

if (-not $success) {
    Write-Host "ERROR: Backend server failed to start or is not responding."
    Write-Host "Killing server process $serverPid..."
    Stop-Process -Id $serverPid -Force -ErrorAction SilentlyContinue
    Write-Host "Checking for other processes on port 8000..."
    $portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
    if ($portProcess) {
        Write-Host "Other processes still using port 8000: $($portProcess.OwningProcess)"
    }
    exit 1
} else {
    # Keep server running - wait for user to press Ctrl+C
    Write-Host "`nBackend server is running. Press Ctrl+C to stop."
    try {
        Wait-Process -Id $serverPid -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Server stopped."
    }
}