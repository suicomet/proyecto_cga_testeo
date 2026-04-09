@echo off
REM Script batch para verificar el backend Django
echo Verificando configuración del backend Django...
powershell -ExecutionPolicy Bypass -File "%~dp0verify-backend.ps1" %*
pause