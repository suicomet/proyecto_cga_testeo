from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    Turno, Distribucion, Insumo, TipoProduccion, JornadaDiaria, Produccion,
    MovimientoBodega, ConteoBodega, Cliente, Producto, Pedido, DetallePedido,
    DetalleMovimiento
)
from .serializers import (
    TurnoSerializer, DistribucionSerializer, InsumoSerializer, TipoProduccionSerializer,
    JornadaDiariaSerializer, ProduccionSerializer, MovimientoBodegaSerializer,
    ConteoBodegaSerializer, ClienteSerializer, ProductoSerializer, PedidoSerializer,
    DetallePedidoSerializer, DetalleMovimientoSerializer
)


class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DistribucionViewSet(viewsets.ModelViewSet):
    queryset = Distribucion.objects.all()
    serializer_class = DistribucionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TipoProduccionViewSet(viewsets.ModelViewSet):
    queryset = TipoProduccion.objects.all()
    serializer_class = TipoProduccionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class JornadaDiariaViewSet(viewsets.ModelViewSet):
    queryset = JornadaDiaria.objects.all()
    serializer_class = JornadaDiariaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProduccionViewSet(viewsets.ModelViewSet):
    queryset = Produccion.objects.all()
    serializer_class = ProduccionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MovimientoBodegaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoBodega.objects.all()
    serializer_class = MovimientoBodegaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ConteoBodegaViewSet(viewsets.ModelViewSet):
    queryset = ConteoBodega.objects.all()
    serializer_class = ConteoBodegaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def saldo(self, request, pk=None):
        cliente = self.get_object()
        
        movimientos = DetalleMovimiento.objects.filter(id_cliente=cliente)
        
        saldo_acumulado = movimientos.aggregate(
            total_venta=Coalesce(Sum(F('precio_cobrado') * F('kilos'), output_field=DecimalField()), 0),
            total_pago=Coalesce(Sum('cancelacion', output_field=DecimalField()), 0)
        )
        
        saldo = saldo_acumulado['total_venta'] - saldo_acumulado['total_pago']
        
        return Response({
            'cliente_id': cliente.id_cliente,
            'cliente_nombre': cliente.nombre_cliente,
            'total_venta': saldo_acumulado['total_venta'],
            'total_pago': saldo_acumulado['total_pago'],
            'saldo_acumulado': saldo
        })


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DetalleMovimientoViewSet(viewsets.ModelViewSet):
    queryset = DetalleMovimiento.objects.all()
    serializer_class = DetalleMovimientoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def resumen_jornada(self, request):
        jornada_id = request.query_params.get('jornada_id')
        if not jornada_id:
            return Response({'error': 'jornada_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        movimientos = DetalleMovimiento.objects.filter(id_jornada_id=jornada_id)
        
        resumen = movimientos.values('id_cliente', 'id_cliente__nombre_cliente').annotate(
            total_venta=Sum(F('precio_cobrado') * F('kilos')),
            total_pago=Sum('cancelacion')
        ).annotate(
            saldo_dia=F('total_venta') - F('total_pago')
        )
        
        return Response(list(resumen))


class ReportesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def stock_insumo(self, request):
        insumo_id = request.query_params.get('insumo_id')
        if not insumo_id:
            return Response({'error': 'insumo_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        movimientos = MovimientoBodega.objects.filter(id_insumo_id=insumo_id)
        
        entradas = movimientos.filter(tipo_movimiento='ENTRADA').aggregate(total=Coalesce(Sum('cantidad'), 0))
        salidas = movimientos.filter(tipo_movimiento='SALIDA').aggregate(total=Coalesce(Sum('cantidad'), 0))
        ajustes = movimientos.filter(tipo_movimiento='AJUSTE').aggregate(total=Coalesce(Sum('cantidad'), 0))
        
        stock_teorico = entradas['total'] - salidas['total'] + ajustes['total']
        
        ultimo_conteo = ConteoBodega.objects.filter(id_insumo_id=insumo_id).order_by('-fecha_conteo').first()
        
        return Response({
            'insumo_id': insumo_id,
            'stock_teorico': stock_teorico,
            'ultimo_conteo': ultimo_conteo.cantidad_fisica if ultimo_conteo else None,
            'fecha_ultimo_conteo': ultimo_conteo.fecha_conteo if ultimo_conteo else None,
            'diferencia': stock_teorico - (ultimo_conteo.cantidad_fisica if ultimo_conteo else 0)
        })