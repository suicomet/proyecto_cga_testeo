from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'turnos', views.TurnoViewSet)
router.register(r'distribuciones', views.DistribucionViewSet)
router.register(r'insumos', views.InsumoViewSet)
router.register(r'tipos-produccion', views.TipoProduccionViewSet)
router.register(r'jornadas', views.JornadaDiariaViewSet)
router.register(r'producciones', views.ProduccionViewSet)
router.register(r'movimientos-bodega', views.MovimientoBodegaViewSet)
router.register(r'conteos-bodega', views.ConteoBodegaViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'pedidos', views.PedidoViewSet)
router.register(r'detalles-pedido', views.DetallePedidoViewSet)
router.register(r'movimientos', views.DetalleMovimientoViewSet)
router.register(r'reportes', views.ReportesViewSet, basename='reportes')

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('', include(router.urls)),
]