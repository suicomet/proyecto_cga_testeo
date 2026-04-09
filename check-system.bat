@echo off
echo === VERIFICACION SISTEMA PANADERIA ===
echo Fecha: %date% %time%
echo.

echo 1. Verificando PostgreSQL...
tasklist | findstr postgres > nul
if %errorlevel% equ 0 (
    echo    OK: PostgreSQL esta ejecutandose
) else (
    echo    ERROR: PostgreSQL NO esta ejecutandose
)

echo 2. Verificando puerto 8000...
netstat -ano | findstr :8000 > nul
if %errorlevel% equ 0 (
    echo    ADVERTENCIA: Puerto 8000 en uso
    netstat -ano | findstr :8000
) else (
    echo    OK: Puerto 8000 disponible
)

echo 3. Verificando Node.js...
if exist "C:\Program Files\nodejs\node.exe" (
    echo    OK: Node.js instalado
    "C:\Program Files\nodejs\node.exe" --version
) else (
    echo    ERROR: Node.js NO instalado
)

echo 4. Verificando npm...
if exist "C:\Program Files\nodejs\npm.cmd" (
    echo    OK: npm.cmd encontrado
) else (
    echo    ADVERTENCIA: npm.cmd no encontrado
)

echo 5. Verificando Python y entorno virtual...
if exist "backend\venv\Scripts\python.exe" (
    echo    OK: Entorno virtual Python encontrado
    backend\venv\Scripts\python.exe --version
) else (
    echo    ERROR: NO hay entorno virtual Python
)

echo 6. Verificando Django...
if exist "backend\venv\Scripts\python.exe" if exist "backend\manage.py" (
    echo    OK: manage.py encontrado
    backend\venv\Scripts\python.exe backend\manage.py check
    if %errorlevel% equ 0 (
        echo    OK: Django project check passed
    ) else (
        echo    ERROR: Django project check failed
    )
)

echo 7. Verificando Angular...
if exist "frontend\package.json" if exist "frontend\angular.json" (
    echo    OK: Proyecto Angular encontrado
    if exist "frontend\node_modules" (
        echo    OK: node_modules instalado
    ) else (
        echo    ADVERTENCIA: node_modules no instalado
    )
) else (
    echo    ERROR: Proyecto Angular incompleto
)

echo.
echo === RESUMEN ===
echo.
echo Para probar manualmente:
echo   1. BACKEND: 
echo      cd backend
echo      venv\Scripts\activate.bat
echo      python manage.py runserver
echo.
echo   2. Verificar en navegador:
echo      http://localhost:8000/api/turnos/
echo      http://localhost:8000/admin/
echo.
echo   3. FRONTEND:
echo      cd frontend
echo      npm start
echo.
echo   4. Verificar en navegador:
echo      http://localhost:4200/
echo.
echo Usuario demo Django: admin / admin123