# Backend Panadería - Django + PostgreSQL

## Requisitos Previos
- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes Python)

## Instalación

### 1. Configurar entorno virtual
```bash
cd backend
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos PostgreSQL
1. Asegúrate que PostgreSQL esté instalado y corriendo
2. Crea la base de datos:
   ```bash
   psql -U postgres -f scripts/setup_database.sql
   ```
3. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales de PostgreSQL
   ```

### 4. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Cargar datos iniciales
```bash
python manage.py load_initial_data
```

### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

## Estructura del Proyecto
```
backend/
├── api/                    # Aplicación principal
│   ├── management/commands/
│   │   └── load_initial_data.py
│   ├── migrations/         # Migraciones de base de datos
│   ├── __init__.py
│   ├── admin.py           # Configuración del admin
│   ├── apps.py
│   ├── models.py          # 17 modelos según especificación
│   ├── serializers.py     # Serializadores DRF
│   ├── urls.py            # Rutas de la API
│   └── views.py           # Vistas de la API
├── panaderia_backend/     # Configuración del proyecto
│   ├── __init__.py
│   ├── settings.py        # Configuración principal
│   ├── urls.py            # Rutas principales
│   ├── asgi.py
│   └── wsgi.py
├── scripts/               # Scripts de utilidad
│   └── setup_database.sql
├── manage.py
├── requirements.txt
└── .env.example
```

## API Endpoints
La API REST está disponible en `http://localhost:8000/api/`

### Autenticación
- `POST /api/token/` - Obtener token JWT
- `POST /api/token/refresh/` - Refrescar token

### Recursos principales
- `GET /api/turnos/` - Catálogo de turnos
- `GET /api/distribuciones/` - Canales de distribución
- `GET /api/clientes/` - Clientes
- `GET /api/productos/` - Productos
- `GET /api/pedidos/` - Pedidos
- `GET /api/movimientos/` - Movimientos diarios
- `GET /api/producciones/` - Producción por jornada

### Endpoints especiales
- `GET /api/clientes/{id}/saldo/` - Saldo acumulado del cliente
- `GET /api/movimientos/resumen_jornada/?jornada_id=X` - Resumen por jornada
- `GET /api/reportes/stock_insumo/?insumo_id=X` - Stock teórico vs físico

## Reglas de Negocio Implementadas
1. **Venta calculada**: `precio_cobrado × kilos` (no se almacena)
2. **Saldo por consulta**: Calculado mediante vistas/consultas
3. **Descuentos opcionales**: Pueden ser NULL o 0-100%
4. **Campos opcionales**: `id_pedido`, `id_jornada`, `id_turno` pueden ser NULL
5. **Constraints PostgreSQL**: 
   - `tipo_movimiento IN ('ENTRADA','SALIDA','AJUSTE')`
   - `descuento_porcentaje_aplicado BETWEEN 0 AND 100`

## Datos Iniciales
- **Turnos**: Noche, Mañana, Tarde
- **Distribución**: Repartidor 1, Repartidor 2, Retiro en panadería, Sala de ventas

## Próximos Pasos
1. Configurar CORS para frontend Angular (ya configurado para localhost:4200)
2. Implementar pruebas unitarias
3. Configurar entorno de producción
4. Implementar backup automático de base de datos