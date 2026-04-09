-- Script para crear base de datos y usuario para el proyecto Panadería
-- Ejecutar como usuario postgres o con permisos de superusuario

-- 1. Crear base de datos
CREATE DATABASE panaderia_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Chile.1252'
    LC_CTYPE = 'Spanish_Chile.1252'
    CONNECTION LIMIT = -1;

-- 2. Crear usuario (opcional, si no quieres usar postgres)
CREATE USER panaderia_user WITH PASSWORD 'panaderia_pass';
GRANT ALL PRIVILEGES ON DATABASE panaderia_db TO panaderia_user;

-- 3. Conectarse a la base de datos panaderia_db y configurar permisos adicionales
-- \c panaderia_db
-- GRANT ALL ON SCHEMA public TO panaderia_user;