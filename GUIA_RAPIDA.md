# Guía Rápida - Poner en Marcha el Sistema

## 📋 Estado del Proyecto
El **backend Django con PostgreSQL** ya está **completamente configurado y funcionando** con datos de prueba. Solo falta instalar Node.js para el frontend Angular.

## 🚀 Pasos para Ejecutar el Sistema

### Paso 1: Verificar Backend (Django + PostgreSQL)
```cmd
cd E:\panaderia_proyecto\backend
venv\Scripts\activate.bat
python manage.py runserver
```

**Verificar funcionamiento**:
- API: http://localhost:8000/api/turnos/
- Admin: http://localhost:8000/admin
  - Usuario: `admin`
  - Contraseña: `admin123`

### Paso 2: Instalar Node.js (Solo si no está instalado)
#### Opción A: Instalador Oficial (Recomendado)
1. Descargar Node.js 18+ LTS desde https://nodejs.org
2. Ejecutar instalador (.msi)
3. **IMPORTANTE**: Marcar opción **"Add to PATH"**
4. Verificar instalación:
   ```cmd
   node --version
   npm --version
   ```

#### Opción B: Chocolatey (si está instalado)
```cmd
choco install nodejs
```

#### Opción C: Winget (Windows 10/11)
```cmd
winget install OpenJS.NodeJS
```

### Paso 3: Instalar Dependencias Angular
```cmd
cd E:\panaderia_proyecto\frontend
npm install
```

### Paso 4: Ejecutar Frontend
```cmd
npm start
```
- Frontend: http://localhost:4200

### Paso 5: Acceder al Sistema
1. **Frontend**: http://localhost:4200/login
   - Usuario: `admin`
   - Contraseña: `admin123`
2. **Backend API**: http://localhost:8000/api/
3. **Admin Django**: http://localhost:8000/admin

## 🔧 Configuración PostgreSQL
- **Base de datos**: `panaderia_db`
- **Usuario**: `postgres`
- **Contraseña**: `postgres` (configurada en `backend/.env`)
- **Host**: `localhost`
- **Puerto**: `5432`

**Si cambiaste la contraseña durante la instalación de PostgreSQL**, edita `backend/.env` línea 7.

## 📊 Datos de Prueba Incluidos
El sistema incluye datos de prueba listos para usar:
- **Clientes**: Supermercado Los Andes, Restaurante La Familia, etc. (con RUT y descuentos)
- **Productos**: Pan corriente, integral, medialunas, facturas, tortas (con precios)
- **Pedidos**: 10 pedidos con detalles
- **Producción**: Registros por jornada y turno
- **Bodega**: Insumos, movimientos, conteos físicos

## 🧪 Probar Endpoints API Principales
```bash
# Turnos
curl http://localhost:8000/api/turnos/

# Clientes
curl http://localhost:8000/api/clientes/

# Productos
curl http://localhost:8000/api/productos/

# Pedidos
curl http://localhost:8000/api/pedidos/

# Obtener token JWT
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 🚨 Solución de Problemas

### Error: "psql no se reconoce"
```cmd
set PATH=C:\Program Files\PostgreSQL\18\bin;%PATH%
```

### Error: "password authentication failed"
Editar `backend/.env` línea 7 con tu contraseña real de PostgreSQL.

### Error: "Port 8000 already in use"
```cmd
python manage.py runserver 8001
```

### Error: "Port 4200 already in use"
```cmd
npm start -- --port 4201
```

### Error: "npm install" falla
```cmd
npm cache clean --force
npm install --verbose
```

## 📁 Estructura del Proyecto
```
panaderia_proyecto/
├── backend/                 # Django + PostgreSQL (LISTO)
│   ├── api/                # 17 modelos + API REST
│   ├── .env               # Configuración PostgreSQL
│   ├── db.sqlite3         # NO USAR (SQLite temporal)
│   └── manage.py
├── frontend/               # Angular 17 (PENDIENTE NODE.JS)
│   ├── src/app/components/ # 8 componentes
│   └── package.json
├── documentos_apoyo/       # PDF con especificaciones
├── README.md              # Documentación general
├── GUIA_RAPIDA.md         # Esta guía
└── INSTALAR_NODE.md       # Instrucciones Node.js
```

## 🔄 Comandos Útiles

### Backend
```cmd
# Activar entorno virtual
venv\Scripts\activate.bat

# Ejecutar servidor
python manage.py runserver

# Crear más datos de prueba
python manage.py create_test_data

# Cargar datos base (turnos, distribución)
python manage.py load_initial_data

# Crear usuario admin
python manage.py create_demo_user
```

### Frontend
```cmd
# Instalar dependencias (requiere Node.js)
npm install

# Ejecutar servidor desarrollo
npm start

# Compilar para producción
npm run build
```

## 📞 Soporte
- **Backend API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin
- **Frontend**: http://localhost:4200
- **Credenciales**: `admin` / `admin123`

## ⏭️ Próximos Pasos
1. Instalar Node.js siguiendo `INSTALAR_NODE.md`
2. Ejecutar `npm install` en `frontend/`
3. Ejecutar `npm start` para frontend
4. Probar integración completa
5. Personalizar según necesidades específicas