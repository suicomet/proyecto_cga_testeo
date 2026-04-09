@echo off
REM Script simple para ejecutar backend Django
cd backend
call venv\Scripts\activate.bat
python manage.py runserver
pause