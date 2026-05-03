import uuid
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import TwoFactorCode


class TestAuth(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testadmin',
            password='Test123!',
            email='test@example.com'
        )
        self.group = Group.objects.create(name='Administrador')
        self.user.groups.add(self.group)

    def test_login_2fa_obtener_codigo(self):
        res = self.client.post('/api/token/2fa/', {
            'username': 'testadmin', 'password': 'Test123!'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('session_id', res.data)
        self.assertIn('Código enviado', res.data['message'])
        self.assertEqual(res.data['expires_in'], 300)

    def test_login_2fa_credenciales_invalidas(self):
        res = self.client.post('/api/token/2fa/', {
            'username': 'testadmin', 'password': 'wrong'
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('error', res.data)

    def test_login_2fa_usuario_inactivo(self):
        self.user.is_active = False
        self.user.save()

        res = self.client.post('/api/token/2fa/', {
            'username': 'testadmin', 'password': 'Test123!'
        })
        self.assertEqual(res.status_code, 401)

    def test_login_2fa_verificar_codigo_correcto(self):
        code_obj = TwoFactorCode.objects.create(
            user=self.user,
            code='123456',
            session_id=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        res = self.client.post('/api/token/2fa/verify/', {
            'session_id': str(code_obj.session_id),
            'code': '123456'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_2fa_codigo_incorrecto(self):
        code_obj = TwoFactorCode.objects.create(
            user=self.user,
            code='123456',
            session_id=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        res = self.client.post('/api/token/2fa/verify/', {
            'session_id': str(code_obj.session_id),
            'code': '000000'
        })
        self.assertEqual(res.status_code, 401)

    def test_login_2fa_codigo_expirado(self):
        code_obj = TwoFactorCode.objects.create(
            user=self.user,
            code='123456',
            session_id=uuid.uuid4(),
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        res = self.client.post('/api/token/2fa/verify/', {
            'session_id': str(code_obj.session_id),
            'code': '123456'
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('Código expirado', res.data['error'])

    def test_login_2fa_codigo_usado(self):
        code_obj = TwoFactorCode.objects.create(
            user=self.user,
            code='123456',
            session_id=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=True
        )

        res = self.client.post('/api/token/2fa/verify/', {
            'session_id': str(code_obj.session_id),
            'code': '123456'
        })
        self.assertEqual(res.status_code, 401)

    def test_login_2fa_codigo_se_invalida_al_solicitar_nuevo(self):
        first_code = TwoFactorCode.objects.create(
            user=self.user,
            code='111111',
            session_id=uuid.uuid4(),
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

        self.client.post('/api/token/2fa/', {
            'username': 'testadmin', 'password': 'Test123!'
        })

        first_code.refresh_from_db()
        self.assertTrue(first_code.is_used)

    def test_api_me_autenticado(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        res = self.client.get('/api/me/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['username'], 'testadmin')
        self.assertIn('Administrador', res.data['roles'])

    def test_api_me_no_autenticado(self):
        res = self.client.get('/api/me/')
        self.assertEqual(res.status_code, 401)

    def test_health_check(self):
        res = self.client.get('/api/health/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['status'], 'healthy')
