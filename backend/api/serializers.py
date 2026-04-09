from rest_framework import serializers
from .models import (
    Turno, Distribucion, Insumo, TipoProduccion, JornadaDiaria, Produccion,
    MovimientoBodega, ConteoBodega, Cliente, Producto, Pedido, DetallePedido,
    DetalleMovimiento
)


class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = '__all__'


class DistribucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribucion
        fields = '__all__'


class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = '__all__'


class TipoProduccionSerializer(serializers.ModelSerializer):
    insumo_principal_nombre = serializers.CharField(source='id_insumo_principal.nombre_insumo', read_only=True)
    
    class Meta:
        model = TipoProduccion
        fields = '__all__'


class JornadaDiariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JornadaDiaria
        fields = '__all__'


class ProduccionSerializer(serializers.ModelSerializer):
    tipo_produccion_nombre = serializers.CharField(source='id_tipo_produccion.nombre_tipo_produccion', read_only=True)
    turno_nombre = serializers.CharField(source='id_turno.nombre_turno', read_only=True)
    jornada_fecha = serializers.DateField(source='id_jornada.fecha', read_only=True)
    
    class Meta:
        model = Produccion
        fields = '__all__'


class MovimientoBodegaSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source='id_insumo.nombre_insumo', read_only=True)
    turno_nombre = serializers.CharField(source='id_turno.nombre_turno', read_only=True, allow_null=True)
    
    class Meta:
        model = MovimientoBodega
        fields = '__all__'


class ConteoBodegaSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source='id_insumo.nombre_insumo', read_only=True)
    turno_nombre = serializers.CharField(source='id_turno.nombre_turno', read_only=True, allow_null=True)
    
    class Meta:
        model = ConteoBodega
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    tipo_produccion_nombre = serializers.CharField(source='id_tipo_produccion.nombre_tipo_produccion', read_only=True)
    
    class Meta:
        model = Producto
        fields = '__all__'


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='id_producto.nombre_producto', read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = '__all__'


class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='id_cliente.nombre_cliente', read_only=True)
    distribucion_nombre = serializers.CharField(source='id_distribucion.nombre_distribucion', read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'


class DetalleMovimientoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='id_cliente.nombre_cliente', read_only=True)
    producto_nombre = serializers.CharField(source='id_producto.nombre_producto', read_only=True)
    distribucion_nombre = serializers.CharField(source='id_distribucion.nombre_distribucion', read_only=True)
    jornada_fecha = serializers.DateField(source='id_jornada.fecha', read_only=True)
    venta_linea = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetalleMovimiento
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['venta_linea'] = instance.venta_linea
        return representation