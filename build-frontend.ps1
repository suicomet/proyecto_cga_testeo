# Build frontend
$env:Path = "C:\Program Files\nodejs;$env:Path"
cd frontend
Write-Host "Compilando Angular..." -ForegroundColor Cyan
npm run build -- --configuration development