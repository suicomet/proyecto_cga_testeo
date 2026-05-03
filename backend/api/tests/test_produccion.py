from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import (
    JornadaDiaria, Turno, Insumo, TipoProduccion,
    Produccion, CierreTurno
)


class BaseTest:
    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser('admin', 'a@a.com', 'admin123')
        self.authenticate()
        self.turno = Turno.objects.create(nombre_turno='Mañana')
        self.jornada = JornadaDiaria.objects.create(fecha=date.today())
        self.insumo = Insumo.objects.create(
            nombre_insumo='Harina', unidad_control='kg',
            stock_sugerido_inicial=1000, activo='S'
        )
        self.tipo_prod = TipoProduccion.objects.create(
            nombre_tipo_produccion='Pan corriente',
            id_insumo_principal=self.insumo
        )


class TestJornadas(BaseTest, TestCase):
    def test_crear_jornada(self):
        res = self.client.post('/api/jornadas/', {
            'fecha': str(date(2030, 1, 15))
        })
        self.assertEqual(res.status_code, 201)

    def test_listar_jornadas(self):
        JornadaDiaria.objects.create(fecha=date(2030, 6, 1))
        res = self.client.get('/api/jornadas/')
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_crear_jornada_duplicada(self):
        fecha_str = '2030-12-25'
        self.client.post('/api/jornadas/', {'fecha': fecha_str})
        res = self.client.post('/api/jornadas/', {'fecha': fecha_str})
        self.assertEqual(res.status_code, 400)


class TestProduccion(BaseTest, TestCase):
    def test_crear_produccion(self):
        res = self.client.post('/api/producciones/', {
            'id_jornada': self.jornada.id_jornada,
            'id_tipo_produccion': self.tipo_prod.id_tipo_produccion,
            'id_turno': self.turno.id_turno,
            'quintales': 25.5,
        })
        self.assertEqual(res.status_code, 201)

    def test_listar_producciones(self):
        Produccion.objects.create(
            id_jornada=self.jornada,
            id_tipo_produccion=self.tipo_prod,
            id_turno=self.turno,
            quintales=10
        )
        res = self.client.get('/api/producciones/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)


class TestCierreTurno(BaseTest, TestCase):
    def test_crear_cierre_turno(self):
        res = self.client.post('/api/cierres-turno/', {
            'id_jornada': self.jornada.id_jornada,
            'id_turno': self.turno.id_turno,
            'mostrador_kg': 100,
            'raciones_kg': 50,
            'ajuste_por_error_kg': 0,
            'pan_especial_kg': 0,
            'quintales_cocidos': 30,
            'kilos_directos': 500,
            'unidades_totales': 200,
            'kilos_equivalentes': 150,
            'kilos_totales': 650,
            'rinde': 21.67,
            'estado': 'EN_PROCESO',
        })
        self.assertEqual(res.status_code, 201)

    def test_cerrar_turno_ya_cerrado(self):
        cierre = CierreTurno.objects.create(
            id_jornada=self.jornada,
            id_turno=self.turno,
            estado='CERRADO',
            mostrador_kg=100, raciones_kg=50,
            ajuste_por_error_kg=0, pan_especial_kg=0,
            quintales_cocidos=30, kilos_directos=500,
            unidades_totales=200, kilos_equivalentes=150,
            kilos_totales=650, rinde=21.67,
        )

        res = self.client.post(f'/api/cierres-turno/{cierre.id_cierre_turno}/cerrar/')
        self.assertIn(res.status_code, [400, 403, 409])
