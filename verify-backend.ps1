param(
    [switch]$Full = $false
)

Write-Host "=== PANADERÍA BACKEND VERIFICATION ==="
Write-Host "Date: $(Get-Date)"
Write-Host ""

# 1. Check working directory
Write-Host "1. Checking project structure..."
$backendDir = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendDir)) {
    Write-Host "  ERROR: Backend directory not found: $backendDir" -ForegroundColor Red
    Write-Host "  Please run: cd backend; python -m venv venv"
    exit 1
}
Write-Host "  [OK] Backend directory exists: $backendDir" -ForegroundColor Green

# 2. Check Python virtual environment
Write-Host "2. Checking Python virtual environment..."
$pythonExe = Join-Path $backendDir "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "  ERROR: Python executable not found: $pythonExe" -ForegroundColor Red
    Write-Host "  Please run: cd backend; python -m venv venv"
    exit 1
}
Write-Host "  [OK] Python executable found: $pythonExe" -ForegroundColor Green

# 3. Check Django manage.py
Write-Host "3. Checking Django project..."
$managePy = Join-Path $backendDir "manage.py"
if (-not (Test-Path $managePy)) {
    Write-Host "  ERROR: manage.py not found: $managePy" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] manage.py found: $managePy" -ForegroundColor Green

# 4. Check .env file
Write-Host "4. Checking environment configuration..."
$envFile = Join-Path $backendDir ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "  WARNING: .env file not found: $envFile" -ForegroundColor Yellow
    Write-Host "  Please copy .env.example to .env and configure it."
} else {
    Write-Host "  [OK] .env file found: $envFile" -ForegroundColor Green
}

# 5. Check port 8000
Write-Host "5. Checking port 8000..."
$portProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
if ($portProcess) {
    Write-Host "  WARNING: Port 8000 is in use by process: $($portProcess.OwningProcess)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 8000 is available" -ForegroundColor Green
}

# 6. Check PostgreSQL (if Full mode or PostgreSQL is configured)
Write-Host "6. Checking PostgreSQL..."
$psqlPath = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
if (Test-Path $psqlPath) {
    try {
        # Read database configuration from .env
        $envContent = Get-Content $envFile -ErrorAction SilentlyContinue
        $dbName = "panaderia_db"
        $dbUser = "postgres"
        $dbPassword = "postgres"
        
        if ($envContent) {
            foreach ($line in $envContent) {
                if ($line -match "^DB_NAME=(.+)$") { $dbName = $matches[1] }
                if ($line -match "^DB_USER=(.+)$") { $dbUser = $matches[1] }
                if ($line -match "^DB_PASSWORD=(.+)$") { $dbPassword = $matches[1] }
            }
        }
        
        $env:PGPASSWORD = $dbPassword
        $result = & $psqlPath -h localhost -p 5432 -U $dbUser -d $dbName -c "SELECT version();" -q -t 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] PostgreSQL connection successful to database '$dbName'" -ForegroundColor Green
            
            if ($Full) {
                # Check tables
                $tables = & $psqlPath -h localhost -p 5432 -U $dbUser -d $dbName -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" -q -t
                Write-Host "  [OK] Tables in database: $($tables.Trim())" -ForegroundColor Green
                
                # Check Django migrations
                $migrations = & $psqlPath -h localhost -p 5432 -U $dbUser -d $dbName -c "SELECT COUNT(*) FROM django_migrations;" -q -t
                Write-Host "  [OK] Applied migrations: $($migrations.Trim())" -ForegroundColor Green
            }
        } else {
            Write-Host "  ERROR: PostgreSQL connection failed" -ForegroundColor Red
            Write-Host "  Details: $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ERROR: PostgreSQL check failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  WARNING: PostgreSQL client not found at $psqlPath" -ForegroundColor Yellow
    Write-Host "  PostgreSQL checks skipped." -ForegroundColor Yellow
}

# 7. Run Django system check
Write-Host "7. Running Django system check..."
try {
    $output = & $pythonExe $managePy check 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Django system check passed" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Django system check failed" -ForegroundColor Red
        Write-Host "  Output: $output" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: Failed to run Django check: $_" -ForegroundColor Red
}

# 8. Check for pending migrations
Write-Host "8. Checking Django migrations..."
try {
    $output = & $pythonExe $managePy showmigrations --plan 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pending = ($output | Select-String "\[ \]").Count
        if ($pending -gt 0) {
            Write-Host "  WARNING: $pending pending migrations" -ForegroundColor Yellow
            Write-Host "  Run: python manage.py migrate" -ForegroundColor Yellow
        } else {
            Write-Host "  [OK] All migrations applied" -ForegroundColor Green
        }
    } else {
        Write-Host "  ERROR: Failed to check migrations" -ForegroundColor Red
    }
} catch {
    Write-Host "  ERROR: Failed to check migrations: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== VERIFICATION COMPLETE ==="
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Run setup-backend.ps1 to initialize database and create admin user"
Write-Host "2. Run start-backend.ps1 to start the server"
Write-Host "3. Run start-test-backend.ps1 to test API connectivity"
Write-Host ""
Write-Host "For detailed check, run: .\verify-backend.ps1 -Full"