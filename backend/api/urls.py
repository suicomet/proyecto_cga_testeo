from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .usuarios_views import UsuarioSistemaViewSet


# Router global (backward compatibility)
router = DefaultRouter()
router.register(r'turnos', views.TurnoViewSet)
router.register(r'distribuciones', views.DistribucionViewSet)
router.register(r'insumos', views.InsumoViewSet)
router.register(r'tipos-produccion', views.TipoProduccionViewSet)
router.register(r'jornadas', views.JornadaDiariaViewSet)
router.register(r'producciones', views.ProduccionViewSet)
router.register(r'cierres-turno', views.CierreTurnoViewSet)
router.register(r'movimientos-bodega', views.MovimientoBodegaViewSet)
router.register(r'conteos-bodega', views.ConteoBodegaViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'pedidos', views.PedidoViewSet)
router.register(r'detalles-pedido', views.DetallePedidoViewSet)
router.register(r'movimientos', views.DetalleMovimientoViewSet)
router.register(r'repartos-turno', views.DetalleRepartoTurnoViewSet)
router.register(r'reportes', views.ReportesViewSet, basename='reportes')
router.register(r'usuarios', UsuarioSistemaViewSet, basename='usuarios')


# Módulo Catálogo
router_catalogo = DefaultRouter()
router_catalogo.register(r'turnos', views.TurnoViewSet)
router_catalogo.register(r'distribuciones', views.DistribucionViewSet)
router_catalogo.register(r'insumos', views.InsumoViewSet)
router_catalogo.register(r'tipos-produccion', views.TipoProduccionViewSet)
router_catalogo.register(r'productos', views.ProductoViewSet)


# Módulo Producción
router_produccion = DefaultRouter()
router_produccion.register(r'jornadas', views.JornadaDiariaViewSet)
router_produccion.register(r'producciones', views.ProduccionViewSet)
router_produccion.register(r'cierres-turno', views.CierreTurnoViewSet)
router_produccion.register(r'repartos-turno', views.DetalleRepartoTurnoViewSet)


# Módulo Bodega
router_bodega = DefaultRouter()
router_bodega.register(r'movimientos-bodega', views.MovimientoBodegaViewSet)
router_bodega.register(r'conteos-bodega', views.ConteoBodegaViewSet)


# Módulo Ventas
router_ventas = DefaultRouter()
router_ventas.register(r'clientes', views.ClienteViewSet)
router_ventas.register(r'pedidos', views.PedidoViewSet)
router_ventas.register(r'detalles-pedido', views.DetallePedidoViewSet)
router_ventas.register(r'movimientos', views.DetalleMovimientoViewSet)


# Módulo Reportes
router_reportes = DefaultRouter()
router_reportes.register(r'reportes', views.ReportesViewSet, basename='reportes')


urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('me/', views.usuario_actual, name='usuario-actual'),
    path('token/2fa/', views.two_factor_obtain, name='token-2fa-obtain'),
    path('token/2fa/verify/', views.two_factor_verify, name='token-2fa-verify'),

    path('', include(router.urls)),  # Rutas globales (backward compatibility)
    path('catalogo/', include(router_catalogo.urls)),
    path('produccion/', include(router_produccion.urls)),
    path('bodega/', include(router_bodega.urls)),
    path('ventas/', include(router_ventas.urls)),
    path('reportes/', include(router_reportes.urls)),
]
