param(
    [switch]$Force = $false
)

Write-Host "=== PANADERÍA BACKEND SETUP ==="
Write-Host "Date: $(Get-Date)"
Write-Host ""

# 1. Set variables
$backendDir = Join-Path $PSScriptRoot "backend"
$pythonExe = Join-Path $backendDir "venv\Scripts\python.exe"
$managePy = Join-Path $backendDir "manage.py"

# 2. Verify prerequisites
Write-Host "1. Verifying prerequisites..."

if (-not (Test-Path $pythonExe)) {
    Write-Host "  ERROR: Python virtual environment not found." -ForegroundColor Red
    Write-Host "  Please create it with: cd backend; python -m venv venv" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $managePy)) {
    Write-Host "  ERROR: Django manage.py not found." -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] Python and Django found" -ForegroundColor Green

# 3. Check .env file
Write-Host "2. Checking environment configuration..."
$envFile = Join-Path $backendDir ".env"
$envExample = Join-Path $backendDir ".env.example"

if (-not (Test-Path $envFile)) {
    Write-Host "  .env file not found, creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  [OK] .env file created from .env.example" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: .env.example not found" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  [OK] .env file exists" -ForegroundColor Green
}

# 4. Check PostgreSQL connection
Write-Host "3. Checking PostgreSQL connection..."
$psqlPath = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
if (Test-Path $psqlPath) {
    try {
        # Read database configuration
        $envContent = Get-Content $envFile -ErrorAction SilentlyContinue
        $dbName = "panaderia_db"
        $dbUser = "postgres"
        $dbPassword = "postgres"
        
        foreach ($line in $envContent) {
            if ($line -match "^DB_NAME=(.+)$") { $dbName = $matches[1] }
            if ($line -match "^DB_USER=(.+)$") { $dbUser = $matches[1] }
            if ($line -match "^DB_PASSWORD=(.+)$") { $dbPassword = $matches[1] }
        }
        
        $env:PGPASSWORD = $dbPassword
        Write-Host "  Testing connection to database '$dbName' as user '$dbUser'..."
        $result = & $psqlPath -h localhost -p 5432 -U $dbUser -d postgres -c "SELECT 1" -q -t 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] PostgreSQL connection successful" -ForegroundColor Green
            
            # Check if database exists
            $dbExists = & $psqlPath -h localhost -p 5432 -U $dbUser -d postgres -c "SELECT 1 FROM pg_database WHERE datname='$dbName'" -q -t 2>&1
            if ($dbExists.Trim() -ne "1") {
                Write-Host "  Database '$dbName' does not exist, creating..." -ForegroundColor Yellow
                
                # Try to create database
                $createResult = & $psqlPath -h localhost -p 5432 -U $dbUser -d postgres -c "CREATE DATABASE $dbName;" -q -t 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  [OK] Database '$dbName' created" -ForegroundColor Green
                } else {
                    Write-Host "  ERROR: Failed to create database: $createResult" -ForegroundColor Red
                    if (-not $Force) {
                        exit 1
                    }
                }
            } else {
                Write-Host "  [OK] Database '$dbName' exists" -ForegroundColor Green
            }
        } else {
            Write-Host "  ERROR: PostgreSQL connection failed" -ForegroundColor Red
            Write-Host "  Please ensure PostgreSQL is running and credentials in .env are correct." -ForegroundColor Red
            if (-not $Force) {
                exit 1
            }
        }
    } catch {
        Write-Host "  ERROR: PostgreSQL check failed: $_" -ForegroundColor Red
        if (-not $Force) {
            exit 1
        }
    }
} else {
    Write-Host "  WARNING: PostgreSQL client not found, skipping database checks" -ForegroundColor Yellow
}

# 5. Run Django migrations
Write-Host "4. Applying Django migrations..."
try {
    $output = & $pythonExe $managePy migrate 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Migrations applied successfully" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: Failed to apply migrations" -ForegroundColor Red
        Write-Host "  Output: $output" -ForegroundColor Red
        if (-not $Force) {
            exit 1
        }
    }
} catch {
    Write-Host "  ERROR: Failed to run migrations: $_" -ForegroundColor Red
    if (-not $Force) {
        exit 1
    }
}

# 6. Create admin user
Write-Host "5. Creating admin user..."
try {
    $output = & $pythonExe $managePy create_demo_user 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Admin user created or already exists" -ForegroundColor Green
        Write-Host "  Username: admin, Password: admin123" -ForegroundColor Cyan
    } else {
        Write-Host "  WARNING: Failed to create admin user: $output" -ForegroundColor Yellow
        Write-Host "  You can create it manually with: python manage.py createsuperuser" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  WARNING: Failed to create admin user: $_" -ForegroundColor Yellow
}

# 7. Load initial data
Write-Host "6. Loading initial data..."
try {
    $output = & $pythonExe $managePy load_initial_data 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Initial data loaded" -ForegroundColor Green
        Write-Host "  Turnos: Noche, Mañana, Tarde" -ForegroundColor Cyan
        Write-Host "  Distribuciones: Repartidor 1, Repartidor 2, Retiro en panadería, Sala de ventas" -ForegroundColor Cyan
    } else {
        Write-Host "  WARNING: Failed to load initial data: $output" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  WARNING: Failed to load initial data: $_" -ForegroundColor Yellow
}

# 8. Final verification
Write-Host "7. Final verification..."
try {
    $output = & $pythonExe $managePy check 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Django system check passed" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Django system check failed: $output" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  WARNING: Failed to run system check: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== SETUP COMPLETE ==="
Write-Host ""
Write-Host "Backend setup completed successfully!"
Write-Host ""
Write-Host "To start the backend server:"
Write-Host "  Option 1: .\start-backend.ps1"
Write-Host "  Option 2: .\start.bat"
Write-Host "  Option 3: cd backend && venv\Scripts\activate.bat && python manage.py runserver"
Write-Host ""
Write-Host "To test the API:"
Write-Host "  .\start-test-backend.ps1"
Write-Host ""
Write-Host "To verify everything:"
Write-Host "  .\verify-backend.ps1 -Full"
Write-Host ""
Write-Host "Access URLs:"
Write-Host "  API: http://localhost:8000/api/"
Write-Host "  Admin: http://localhost:8000/admin/"
Write-Host "  Admin credentials: admin / admin123"
Write-Host ""