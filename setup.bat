@echo off
REM Script batch para configurar el backend Django
echo Configurando backend Django...
echo.
echo Este script realizará:
echo 1. Verificación de requisitos
echo 2. Configuración de base de datos
echo 3. Aplicación de migraciones
echo 4. Creación de usuario admin
echo 5. Carga de datos iniciales
echo.
echo Para forzar la instalación (ignorar errores menores), ejecutar: setup.bat -Force
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0setup-backend.ps1" %*
pause