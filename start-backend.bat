@echo off
REM Script batch para iniciar el backend Django
REM Usa PowerShell con politica bypass para ejecutar el script .ps1

echo Iniciando backend Django...
powershell -ExecutionPolicy Bypass -File "%~dp0start-backend.ps1"
pause