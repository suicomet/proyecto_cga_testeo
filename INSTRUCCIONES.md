# Instrucciones de Instalación y Uso - Sistema de Panadería

## Estado Actual
✅ **Backend Django** configurado y funcionando con **PostgreSQL 18**
✅ **Base de datos** migrada y con datos iniciales cargados  
✅ **Usuario demo** creado: `admin` / `admin123`
✅ **API REST** funcionando en http://localhost:8000/api/
✅ **Constraints PostgreSQL** implementados según especificaciones
✅ **psycopg2-binary** instalado con wheels precompilados

## Pasos para Ejecutar el Sistema

### 1. Backend Django con PostgreSQL
```cmd
cd E:\panaderia_proyecto\backend
venv\Scripts\activate.bat
python manage.py runserver
```

**Acceso**:
- API: http://localhost:8000/api/
- Admin Django: http://localhost:8000/admin (usuario: `admin`, contraseña: `admin123`)

### 2. Frontend Angular (Requiere Node.js)
**Primero instalar Node.js**:
1. Descargar Node.js 18+ desde https://nodejs.org
2. Instalar con opciones predeterminadas
3. Verificar instalación:
   ```cmd
   node --version
   npm --version
   ```

**Instalar dependencias Angular**:
```cmd
cd E:\panaderia_proyecto\frontend
npm install
```

**Ejecutar servidor frontend**:
```cmd
npm start
```
- Frontend: http://localhost:4200

### 3. Credenciales de Acceso
- **Usuario Django Admin**: `admin`
- **Contraseña Django Admin**: `admin123`
- **Usuario PostgreSQL**: `postgres`
- **Contraseña PostgreSQL**: `postgres` (configurada en `.env`)
- **API Token**: Usar endpoint `/api/token/` para obtener JWT

## Configuración PostgreSQL Implementada

### Base de Datos
- **Nombre**: `panaderia_db`
- **Usuario**: `postgres`
- **Contraseña**: `postgres` (verificar si cambiaste durante instalación)
- **Host**: `localhost`
- **Puerto**: `5432`

### Constraints PostgreSQL Implementados
1. **movimiento_bodega.tipo_movimiento**: Solo `ENTRADA`, `SALIDA` o `AJUSTE`
2. **descuento_porcentaje_aplicado**: Valores entre 0 y 100 (NULL permitido)
3. **Validadores Django**: `MinValueValidator(0)`, `MaxValueValidator(100)`

## Endpoints API Principales
- `GET /api/turnos/` - Catálogo de turnos (Noche, Mañana, Tarde)
- `GET /api/distribuciones/` - Canales de distribución
- `GET /api/clientes/` - Lista de clientes con RUT y descuentos
- `GET /api/productos/` - Catálogo de productos con precios sugeridos
- `GET /api/pedidos/` - Pedidos registrados con detalles
- `GET /api/movimientos/` - Movimientos diarios con cálculo de ventas
- `GET /api/producciones/` - Registro de producción por jornada/turno
- `POST /api/token/` - Obtener token JWT para autenticación

## Endpoints Especiales
- `GET /api/clientes/{id}/saldo/` - Saldo acumulado del cliente
- `GET /api/movimientos/resumen_jornada/?jornada_id=X` - Resumen por jornada
- `GET /api/reportes/stock_insumo/?insumo_id=X` - Stock teórico vs físico

## Datos Iniciales Cargados
- **Turnos**: Noche, Mañana, Tarde
- **Distribución**: Repartidor 1, Repartidor 2, Retiro en panadería, Sala de ventas

## Estructura del Proyecto
```
panaderia_proyecto/
├── backend/                 # Django + PostgreSQL
│   ├── api/                # 17 modelos implementados
│   │   ├── models.py       # Modelos con constraints PostgreSQL
│   │   ├── views.py        # API REST + cálculos especiales
│   │   ├── serializers.py  # Serializadores DRF
│   │   └── admin.py        # Configuración Django Admin
│   ├── panaderia_backend/  # Configuración del proyecto
│   │   └── settings.py     # Configurado para PostgreSQL
│   ├── .env               # Variables de entorno (contraseñas)
│   ├── requirements.txt    # psycopg2-binary==2.9.11
│   └── manage.py
├── frontend/               # Angular 17
│   ├── src/app/components/ # 8 componentes principales
│   │   ├── login/         # Autenticación JWT
│   │   ├── dashboard/     # Panel de control
│   │   ├── clientes/      # Gestión de clientes
│   │   ├── productos/     # Catálogo de productos
│   │   ├── pedidos/       # Gestión de pedidos
│   │   ├── produccion/    # Registro de producción
│   │   ├── bodega/        # Control de bodega
│   │   └── reportes/      # Reportes y consultas
│   ├── src/app/services/  # API service + auth interceptor
│   ├── src/app/models/    # Interfaces TypeScript
│   └── package.json
└── INSTRUCCIONES.md       # Este archivo
```

## Verificación de Instalación

### 1. Verificar PostgreSQL
```cmd
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d panaderia_db -c "SELECT version();"
```

### 2. Verificar Backend
```cmd
cd E:\panaderia_proyecto\backend
venv\Scripts\activate.bat
python manage.py check
```

### 3. Probar API
```cmd
curl http://localhost:8000/api/turnos/
```
o en navegador: http://localhost:8000/api/turnos/

## Solución de Problemas

### Error: "password authentication failed"
- Verificar contraseña en `backend/.env` (línea 7: `DB_PASSWORD=postgres`)
- Si usaste otra contraseña durante instalación de PostgreSQL, cambiarla en `.env`

### Error: "psql no se reconoce"
```cmd
set PATH=C:\Program Files\PostgreSQL\18\bin;%PATH%
```

### Error: "Port 8000 already in use"
```cmd
python manage.py runserver 8001
```

### Error: "Port 4200 already in use"
```cmd
npm start -- --port 4201
```

### Error: "Microsoft Visual C++ 14.0 required"
- Ya resuelto usando wheels precompilados de psycopg2-binary
- No se requieren Microsoft C++ Build Tools

## Migración desde SQLite (si aplica)
Si estabas usando SQLite temporalmente:
1. Los datos no se migran automáticamente
2. Ejecutar `python manage.py load_initial_data` para cargar datos base
3. Recrear usuarios con `python manage.py create_demo_user`
4. Los datos de negocio (clientes, productos, etc.) deben ingresarse nuevamente

## Características Implementadas
- ✅ **17 modelos** según esquema congelado del PDF
- ✅ **API REST completa** con Django REST Framework
- ✅ **Autenticación JWT** (token/refresh endpoints)
- ✅ **Cálculos automáticos**: venta = precio_cobrado × kilos
- ✅ **Saldos por consulta**: sum(venta) - sum(pago)
- ✅ **Constraints PostgreSQL** a nivel base de datos
- ✅ **Campos opcionales**: id_pedido, id_jornada, id_turno NULL permitido
- ✅ **Frontend Angular** con componentes para todos los módulos

## Próximos Pasos
1. Instalar Node.js y ejecutar frontend Angular
2. Probar integración completa frontend-backend
3. Agregar más datos de prueba (clientes, productos, movimientos)
4. Personalizar interfaz según necesidades específicas
5. Configurar entorno de producción para despliegue