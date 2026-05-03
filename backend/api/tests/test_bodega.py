from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Insumo, MovimientoBodega, ConteoBodega, JornadaDiaria, Turno


class BaseTest:
    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser('admin', 'a@a.com', 'admin123')
        self.authenticate()
        self.insumo = Insumo.objects.create(
            nombre_insumo='Harina', unidad_control='kg',
            stock_sugerido_inicial=1000, activo='S'
        )
        self.turno = Turno.objects.create(nombre_turno='Mañana')
        self.jornada = JornadaDiaria.objects.create(fecha=date.today())


class TestMovimientosBodega(BaseTest, TestCase):
    def test_listar_movimientos(self):
        MovimientoBodega.objects.create(
            id_insumo=self.insumo, fecha_movimiento=date.today(),
            tipo_movimiento='ENTRADA', cantidad=100,
            id_jornada=self.jornada
        )
        res = self.client.get('/api/movimientos-bodega/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_crear_entrada_stock(self):
        res = self.client.post('/api/movimientos-bodega/', {
            'id_insumo': self.insumo.id_insumo,
            'fecha_movimiento': str(date.today()),
            'tipo_movimiento': 'ENTRADA',
            'cantidad': 500,
            'id_jornada': self.jornada.id_jornada,
        })
        self.assertEqual(res.status_code, 201)
        self.assertEqual(MovimientoBodega.objects.count(), 1)

    def test_crear_salida_stock(self):
        res = self.client.post('/api/movimientos-bodega/', {
            'id_insumo': self.insumo.id_insumo,
            'fecha_movimiento': str(date.today()),
            'tipo_movimiento': 'SALIDA',
            'cantidad': 50,
            'id_jornada': self.jornada.id_jornada,
        })
        self.assertEqual(res.status_code, 201)

    def test_rechazar_tipo_movimiento_invalido(self):
        res = self.client.post('/api/movimientos-bodega/', {
            'id_insumo': self.insumo.id_insumo,
            'fecha_movimiento': str(date.today()),
            'tipo_movimiento': 'INVALIDO',
            'cantidad': 50,
        })
        self.assertEqual(res.status_code, 400)

    def test_movimiento_sin_jornada(self):
        res = self.client.post('/api/movimientos-bodega/', {
            'id_insumo': self.insumo.id_insumo,
            'fecha_movimiento': str(date.today()),
            'tipo_movimiento': 'ENTRADA',
            'cantidad': 100,
        })
        self.assertEqual(res.status_code, 201)


class TestConteoBodega(BaseTest, TestCase):
    def test_crear_conteo(self):
        res = self.client.post('/api/conteos-bodega/', {
            'id_insumo': self.insumo.id_insumo,
            'fecha_conteo': str(date.today()),
            'cantidad_fisica': 950,
            'id_turno': self.turno.id_turno,
        })
        self.assertEqual(res.status_code, 201)

    def test_listar_conteos(self):
        ConteoBodega.objects.create(
            id_insumo=self.insumo, fecha_conteo=date.today(),
            cantidad_fisica=950
        )
        res = self.client.get('/api/conteos-bodega/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
