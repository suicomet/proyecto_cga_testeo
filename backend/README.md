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

---

## Testing

### Resultados actuales — 34/34 tests pasando ✅

```
Módulo              Tests    Estado
─────────────────────────────────────────────
test_auth.py          11    ✅ 11/11  Auth + 2FA + JWT
test_bodega.py         7    ✅  7/7   Movimientos bodega, conteos
test_produccion.py     6    ✅  6/6   Jornadas, producción, cierre turno
test_ventas.py         5    ✅  5/5   Pedidos, movimientos comerciales
test_reportes.py       4    ✅  4/4   Stock insumo, resumen jornada
─────────────────────────────────────────────
Total                 34    ✅ 34/34  Duración: ~20s
```

### Cobertura de funcionalidades

| Funcionalidad | Tests |
|---|---|
| Login 2FA (obtener código) | Verifica que credenciales válidas retornan `session_id` |
| Login 2FA (verificar código) | Verifica que código correcto retorna JWT |
| Login 2FA (código expirado) | Verifica error 401 con código vencido |
| Login 2FA (código incorrecto) | Verifica error 401 con código erróneo |
| Login 2FA (credenciales inválidas) | Verifica error 401 con credenciales incorrectas |
| Login 2FA (invalidación al re-solicitar) | Verifica que código anterior queda inválido al pedir uno nuevo |
| Login 2FA (usuario inactivo) | Verifica error 401 si usuario está desactivado |
| API /me/ autenticado | Verifica que retorna datos del usuario con token válido |
| API /me/ no autenticado | Verifica error 401 sin token |
| Health check | Verifica que endpoint público responde 200 |
| Bodega (CRUD movimientos) | Crear entrada, salida, listar, tipos inválidos |
| Bodega (conteos) | Crear y listar conteos físicos |
| Producción (jornadas) | Crear, listar, evitar duplicados |
| Producción (registro) | Crear y listar producción por jornada/turno |
| Cierre de turno | Crear cierre, error al cerrar ya cerrado |
| Ventas (pedidos) | Crear y listar pedidos |
| Ventas (movimientos) | Crear, listar movimientos y consultar saldo |
| Reportes (stock insumo) | Consultar stock con y sin parámetro |
| Reportes (resumen jornada) | Consultar resumen con y sin parámetro |

### Cómo ejecutar

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar todos los tests (PostgreSQL requerido)
python manage.py test api.tests --keepdb --verbosity=2

# Ejecutar un módulo específico
python manage.py test api.tests.test_auth --keepdb

# Ejecutar un solo test
python manage.py test api.tests.test_auth.TestAuth.test_login_2fa_verificar_codigo_correcto --keepdb
```

**Requisito:** PostgreSQL debe estar corriendo localmente. Los tests crean su propia base de datos temporal (`test_panaderia_db`) y no modifican la base de datos real de desarrollo ni producción.