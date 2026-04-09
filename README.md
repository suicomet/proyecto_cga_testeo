# Sistema de Gestión de Panadería

Sistema web completo para control de producción, pedidos, movimientos reales, pagos y control básico de bodega para una panadería.

## 🚀 Estado Actual del Proyecto

### ✅ **Backend Django** - **COMPLETADO Y FUNCIONANDO**
- **PostgreSQL 18** configurado y conectado
- **17 modelos** implementados según especificaciones del PDF
- **API REST completa** con Django REST Framework
- **Autenticación JWT** implementada
- **Datos de prueba** creados (clientes, productos, pedidos, producción, etc.)
- **Constraints PostgreSQL** implementados según lineamientos
- **Cálculos automáticos**: venta = precio_cobrado × kilos, saldos, stock

### ✅ **Frontend Angular** - **COMPLETADO Y FUNCIONANDO**
- **Node.js v24.14.1** instalado y configurado
- **Dependencias npm** instaladas (802 paquetes)
- **Estructura de componentes** creada (8 componentes principales)
- **Servicios API** configurados con interceptores JWT
- **Routing** completo implementado
- **Interfaz** con Bootstrap 5 lista
- **Proxy configurado** para comunicación con backend
- **Build exitoso** en modo desarrollo

### 📊 **Datos de Prueba Incluidos**
- 6 insumos de bodega (harina, azúcar, levadura, etc.)
- 5 tipos de producción (pan corriente, integral, dulce, etc.)
- 7 productos comerciales con precios
- 5 clientes con RUT y descuentos
- 7 jornadas diarias con producción
- 20 movimientos de bodega
- 10 pedidos con detalles
- Movimientos reales por jornada
- Conteos físicos de bodega

## 🚀 Comienzo Rápido

### ✅ **Sistema completo configurado y funcionando**

#### **Opción 1: Usar scripts automatizados (recomendado)**

1. **Verificar sistema** (diagnóstico completo):
   ```powershell
   .\check-system.bat
   ```

2. **Probar backend** (inicia, prueba y detiene automáticamente):
   ```powershell
   .\test-backend-quick.ps1
   ```

3. **Iniciar sistema completo**:
   - **Backend Django** (en ventana CMD):
     ```cmd
     cd backend
     venv\Scripts\activate.bat
     python manage.py runserver
     ```
   - **Frontend Angular** (en PowerShell):
     ```powershell
     .\start-angular-background.ps1
     ```

4. **Detener sistema completo**:
   ```powershell
   .\stop-system.ps1
   ```

#### **Opción 2: Ejecución manual**

1. **Backend Django** (puerto 8000):
   ```cmd
   cd backend
   venv\Scripts\activate.bat
   python manage.py runserver
   ```

2. **Frontend Angular** (puerto 4200):
   ```powershell
   cd frontend
   npm start
   ```

#### **Acceso inmediato:**
- **Frontend Angular**: http://localhost:4200/
- **Backend API**: http://localhost:8000/api/
- **Admin Django**: http://localhost:8000/admin/

#### **Credenciales demo:**
- **Usuario**: `admin`
- **Contraseña**: `admin123`

**Guía completa**: Consulta [GUIA_RAPIDA.md](GUIA_RAPIDA.md) para instrucciones detalladas paso a paso.

## Stack Tecnológico
- **Frontend**: Angular 17
- **Backend**: Django 4.2 + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)

## Estructura del Proyecto
```
panaderia_proyecto/
├── backend/                 # Aplicación Django
├── frontend/                # Aplicación Angular
├── documentos_apoyo/        # Documentación
└── README.md               # Este archivo
```

## Instalación y Configuración

### 1. Requisitos Previos
- Python 3.8+ y pip
- Node.js 18+ y npm
- PostgreSQL 12+
- Git (opcional)

### 2. Configuración Backend
```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos PostgreSQL
# 1. Crear base de datos 'panaderia_db'
# 2. Configurar .env (copiar .env.example)

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales
python manage.py load_initial_data

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

### 3. Configuración Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm start
```

### 4. Acceso a la Aplicación
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

## Funcionalidades Implementadas

### Módulo Productivo
- Registro de jornadas diarias
- Control de turnos (Noche, Mañana, Tarde)
- Tipos de producción (pan corriente, integral, masa dulce, etc.)
- Registro de producción por jornada y turno
- Control de insumos de bodega
- Movimientos de bodega (entradas, salidas, ajustes)
- Conteos físicos de bodega

### Módulo Comercial
- Catálogo de clientes con RUT y descuentos
- Canales de distribución (reparto, retiro, sala de ventas)
- Catálogo de productos con precios sugeridos
- Gestión de pedidos con detalles
- Registro de movimientos reales del día
- Cálculo automático de ventas (precio_cobrado × kilos)
- Control de pagos y saldos

### Características Técnicas
- **API REST completa** con autenticación JWT
- **Cálculos en tiempo real**: saldos, stock, ventas
- **Constraints PostgreSQL** para validación de datos
- **Interfaz responsive** con Bootstrap 5
- **CORS configurado** para comunicación frontend-backend
- **Admin Django** para gestión administrativa

## Reglas de Negocio Implementadas

### Precios y Descuentos
- Precio sugerido por producto (editable)
- Descuento por cliente (sugerido, editable por operador)
- Precio final cobrado almacenado en cada transacción

### Ventas y Pagos
- Venta calculada: `precio_cobrado × kilos` (no se almacena como campo)
- Pago del día registrado en `cancelacion`
- Saldo calculado por consultas: `sum(venta) - sum(pago)`

### Bodega y Stock
- Stock teórico calculado: `entradas - salidas ± ajustes`
- Conteos físicos para comparación
- Movimientos con jornada/turno opcionales

## Endpoints API Principales

### Autenticación
- `POST /api/token/` - Obtener token JWT
- `POST /api/token/refresh/` - Refrescar token

### Recursos CRUD
- `/api/clientes/` - Gestión de clientes
- `/api/productos/` - Catálogo de productos
- `/api/pedidos/` - Pedidos y detalles
- `/api/movimientos/` - Movimientos diarios
- `/api/producciones/` - Registro de producción
- `/api/movimientos-bodega/` - Movimientos de bodega

### Reportes Especiales
- `GET /api/clientes/{id}/saldo/` - Saldo acumulado del cliente
- `GET /api/movimientos/resumen_jornada/` - Resumen por jornada
- `GET /api/reportes/stock_insumo/` - Stock teórico vs físico

## Datos Iniciales
- **Turnos**: Noche, Mañana, Tarde
- **Distribución**: Repartidor 1, Repartidor 2, Retiro en panadería, Sala de ventas

## Próximas Mejoras
1. Dashboard con gráficos estadísticos
2. Exportación de reportes a Excel/PDF
3. Notificaciones y recordatorios
4. Integración con sistemas de pago
5. App móvil para repartidores

## Licencia
Proyecto académico - Uso educativo