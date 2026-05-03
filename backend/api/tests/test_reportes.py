from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import (
    Insumo, MovimientoBodega, ConteoBodega, JornadaDiaria, Turno
)


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
        self.jornada = JornadaDiaria.objects.create(fecha=date.today())
        self.turno = Turno.objects.create(nombre_turno='Mañana')


class TestReportes(BaseTest, TestCase):
    def test_stock_insumo_requiere_parametro(self):
        res = self.client.get('/api/reportes/stock_insumo/')
        self.assertEqual(res.status_code, 400)

    def test_stock_insumo_con_parametro(self):
        MovimientoBodega.objects.create(
            id_insumo=self.insumo, fecha_movimiento=date.today(),
            tipo_movimiento='ENTRADA', cantidad=500,
            id_jornada=self.jornada
        )
        ConteoBodega.objects.create(
            id_insumo=self.insumo, fecha_conteo=date.today(),
            cantidad_fisica=950, id_turno=self.turno
        )

        res = self.client.get(
            f'/api/reportes/stock_insumo/?insumo_id={self.insumo.id_insumo}'
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('stock_teorico', res.data)
        self.assertIn('ultimo_conteo', res.data)

    def test_resumen_jornada_requiere_parametro(self):
        res = self.client.get('/api/movimientos/resumen_jornada/')
        self.assertEqual(res.status_code, 400)

    def test_resumen_jornada_con_parametro(self):
        res = self.client.get(
            f'/api/movimientos/resumen_jornada/?jornada_id={self.jornada.id_jornada}'
        )
        self.assertEqual(res.status_code, 200)
