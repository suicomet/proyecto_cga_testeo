from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import (
    Cliente, Producto, Pedido, DetallePedido, DetalleMovimiento,
    JornadaDiaria, Turno, Distribucion, Insumo, TipoProduccion
)


class BaseTest:
    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser('admin', 'a@a.com', 'admin123')
        self.authenticate()
        self.jornada = JornadaDiaria.objects.create(fecha=date.today())
        self.turno = Turno.objects.create(nombre_turno='Mañana')
        self.distribucion = Distribucion.objects.create(nombre_distribucion='Repartidor 1')
        self.cliente = Cliente.objects.create(
            rut=12345678, digito_verificador='9',
            nombre_cliente='Test Cliente', ciudad='Santiago',
            direccion='Av. Test 123', descuento_aplicado=5
        )
        self.insumo = Insumo.objects.create(
            nombre_insumo='Harina', unidad_control='kg',
            stock_sugerido_inicial=1000, activo='S'
        )
        self.tipo_prod = TipoProduccion.objects.create(
            nombre_tipo_produccion='Pan corriente',
            id_insumo_principal=self.insumo
        )
        self.producto = Producto.objects.create(
            nombre_producto='Pan Test', precio_sugerido=2500,
            unidad_venta_base='KILO', id_tipo_produccion=self.tipo_prod
        )


class TestPedidos(BaseTest, TestCase):
    def test_crear_pedido(self):
        res = self.client.post('/api/pedidos/', {
            'id_cliente': self.cliente.id_cliente,
            'id_distribucion': self.distribucion.id_distribucion,
            'fecha_pedido': str(date.today()),
            'fecha_entrega_solicitada': str(date.today()),
        })
        self.assertEqual(res.status_code, 201)

    def test_listar_pedidos(self):
        Pedido.objects.create(
            id_cliente=self.cliente, id_distribucion=self.distribucion,
            fecha_pedido=date.today(), fecha_entrega_solicitada=date.today()
        )
        res = self.client.get('/api/pedidos/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class TestDetalleMovimiento(BaseTest, TestCase):
    def test_crear_movimiento_venta(self):
        res = self.client.post('/api/movimientos/', {
            'id_jornada': self.jornada.id_jornada,
            'id_cliente': self.cliente.id_cliente,
            'id_distribucion': self.distribucion.id_distribucion,
            'id_producto': self.producto.id_producto,
            'precio_cobrado': 2375,
            'cantidad_entregada': 50,
            'unidad_medida': 'KILO',
        })
        self.assertEqual(res.status_code, 201)

    def test_listar_movimientos(self):
        DetalleMovimiento.objects.create(
            id_jornada=self.jornada, id_cliente=self.cliente,
            id_distribucion=self.distribucion, id_producto=self.producto,
            precio_cobrado=2375, cantidad_entregada=50, unidad_medida='KILO'
        )
        res = self.client.get('/api/movimientos/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_saldo_cliente(self):
        DetalleMovimiento.objects.create(
            id_jornada=self.jornada, id_cliente=self.cliente,
            id_distribucion=self.distribucion, id_producto=self.producto,
            precio_cobrado=2375, cantidad_entregada=50, unidad_medida='KILO',
            cancelacion=50000
        )
        res = self.client.get(f'/api/clientes/{self.cliente.id_cliente}/saldo/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('saldo_acumulado', res.data)
        self.assertIn('cliente_nombre', res.data)
