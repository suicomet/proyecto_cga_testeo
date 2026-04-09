from django.contrib import admin
from .models import (
    Turno, Distribucion, Insumo, TipoProduccion, JornadaDiaria, Produccion,
    MovimientoBodega, ConteoBodega, Cliente, Producto, Pedido, DetallePedido,
    DetalleMovimiento
)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id_turno', 'nombre_turno')


@admin.register(Distribucion)
class DistribucionAdmin(admin.ModelAdmin):
    list_display = ('id_distribucion', 'nombre_distribucion')


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('id_insumo', 'nombre_insumo', 'unidad_control', 'stock_sugerido_inicial', 'activo')
    list_filter = ('activo',)


@admin.register(TipoProduccion)
class TipoProduccionAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_produccion', 'nombre_tipo_produccion', 'id_insumo_principal')
    list_filter = ('id_insumo_principal',)


@admin.register(JornadaDiaria)
class JornadaDiariaAdmin(admin.ModelAdmin):
    list_display = ('id_jornada', 'fecha')
    ordering = ('-fecha',)


@admin.register(Produccion)
class ProduccionAdmin(admin.ModelAdmin):
    list_display = ('id_produccion', 'id_jornada', 'id_tipo_produccion', 'id_turno', 'quintales')
    list_filter = ('id_turno', 'id_tipo_produccion')


@admin.register(MovimientoBodega)
class MovimientoBodegaAdmin(admin.ModelAdmin):
    list_display = ('id_movimiento_bodega', 'id_insumo', 'fecha_movimiento', 'tipo_movimiento', 'cantidad', 'id_jornada', 'id_turno')
    list_filter = ('tipo_movimiento', 'id_insumo')
    ordering = ('-fecha_movimiento',)


@admin.register(ConteoBodega)
class ConteoBodegaAdmin(admin.ModelAdmin):
    list_display = ('id_conteo_bodega', 'id_insumo', 'fecha_conteo', 'id_turno', 'cantidad_fisica')
    list_filter = ('id_turno', 'id_insumo')
    ordering = ('-fecha_conteo',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'rut', 'digito_verificador', 'nombre_cliente', 'ciudad', 'telefono', 'descuento_aplicado')
    search_fields = ('nombre_cliente', 'rut')
    list_filter = ('ciudad',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre_producto', 'precio_sugerido', 'id_tipo_produccion')
    search_fields = ('nombre_producto',)
    list_filter = ('id_tipo_produccion',)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'id_cliente', 'id_distribucion', 'fecha_pedido', 'fecha_entrega_solicitada')
    list_filter = ('id_distribucion', 'fecha_pedido')
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_pedido', 'id_pedido', 'id_producto', 'cantidad_solicitada', 'precio_cobrado', 'descuento_porcentaje_aplicado')
    list_filter = ('id_producto',)


@admin.register(DetalleMovimiento)
class DetalleMovimientoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle', 'id_jornada', 'id_cliente', 'id_producto', 'precio_cobrado', 'kilos', 'cancelacion', 'venta_linea')
    list_filter = ('id_jornada', 'id_cliente', 'id_producto')
    ordering = ('-id_jornada__fecha',)
    
    def venta_linea(self, obj):
        return obj.venta_linea
    venta_linea.short_description = 'Venta Línea'