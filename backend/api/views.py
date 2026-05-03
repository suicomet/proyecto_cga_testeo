import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import connection, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.dateparse import parse_date

from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Turno,
    Distribucion,
    Insumo,
    TipoProduccion,
    JornadaDiaria,
    Produccion,
    CierreTurno,
    MovimientoBodega,
    ConteoBodega,
    Cliente,
    Producto,
    Pedido,
    DetallePedido,
    DetalleMovimiento,
    DetalleRepartoTurno,
    ResumenClienteDia,
    SaldoAcumuladoCliente,
    TwoFactorCode,
)

from .serializers import (
    TurnoSerializer,
    DistribucionSerializer,
    InsumoSerializer,
    TipoProduccionSerializer,
    JornadaDiariaSerializer,
    ProduccionSerializer,
    CierreTurnoSerializer,
    MovimientoBodegaSerializer,
    ConteoBodegaSerializer,
    ClienteSerializer,
    ProductoSerializer,
    PedidoSerializer,
    DetallePedidoSerializer,
    DetalleMovimientoSerializer,
    TwoFactorLoginSerializer,
    TwoFactorVerifySerializer,
    DetalleRepartoTurnoSerializer,
)

from .email_utils import enviar_codigo_2fa

from .permissions import (
    EstaAutenticadoLecturaORolEscritura,
    EstaAutenticadoYConRol,
)

# =========================================================
# ROLES OFICIALES DEL SISTEMA
# =========================================================

ROL_ADMINISTRADOR = "Administrador"
ROL_ENCARGADO_TURNO = "Encargado de turno"

ROLES_ADMIN = [ROL_ADMINISTRADOR]
ROLES_OPERACION = [ROL_ADMINISTRADOR, ROL_ENCARGADO_TURNO]

# =========================================================
# CATÁLOGOS BASE
# =========================================================

class TurnoViewSet(viewsets.ModelViewSet):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class DistribucionViewSet(viewsets.ModelViewSet):
    queryset = Distribucion.objects.all()
    serializer_class = DistribucionSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


class TipoProduccionViewSet(viewsets.ModelViewSet):
    queryset = TipoProduccion.objects.all()
    serializer_class = TipoProduccionSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN

    def get_permissions(self):
        if getattr(self, "action", None) == "create":
            self.roles_escritura = ROLES_OPERACION
        else:
            self.roles_escritura = ROLES_ADMIN

        return super().get_permissions()

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN


# =========================================================
# PRODUCCIÓN
# =========================================================

class JornadaDiariaViewSet(viewsets.ModelViewSet):
    queryset = JornadaDiaria.objects.all()
    serializer_class = JornadaDiariaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class ProduccionViewSet(viewsets.ModelViewSet):
    queryset = Produccion.objects.all()
    serializer_class = ProduccionSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class CierreTurnoViewSet(viewsets.ModelViewSet):
    queryset = (
        CierreTurno.objects
        .select_related("id_jornada", "id_turno")
        .all()
        .order_by("-id_jornada__fecha", "id_turno__id_turno")
    )
    serializer_class = CierreTurnoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION

    TIPO_PAN_CORRIENTE = "Pan corriente"
    TIPO_PAN_ESPECIAL = "Pan especial"

    def _decimal_2(self, valor):
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _decimal_4(self, valor):
        return Decimal(valor).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def _usuario_es_admin(self, request):
        usuario = request.user

        if not usuario or not usuario.is_authenticated:
            return False

        if usuario.is_superuser:
            return True

        return usuario.groups.filter(name=ROL_ADMINISTRADOR).exists()

    def _respuesta_cierre_bloqueado(self):
        return Response(
            {
                "detail": (
                    "El cierre ya está cerrado y no se puede editar directamente. "
                    "Debe reabrirse primero."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _sumar_movimientos_pan_corriente(self, cierre, unidad_medida):
        total = (
            DetalleMovimiento.objects
            .filter(
                id_jornada=cierre.id_jornada,
                id_turno=cierre.id_turno,
                id_producto__id_tipo_produccion__nombre_tipo_produccion=self.TIPO_PAN_CORRIENTE,
                unidad_medida=unidad_medida,
            )
            .aggregate(total=Sum("cantidad_entregada"))
        )["total"]

        return self._decimal_2(total or Decimal("0.00"))

    def _sumar_quintales_cocidos(self, cierre):
        total = (
            Produccion.objects
            .filter(
                id_jornada=cierre.id_jornada,
                id_turno=cierre.id_turno,
                id_tipo_produccion__nombre_tipo_produccion__in=[
                    self.TIPO_PAN_CORRIENTE,
                    self.TIPO_PAN_ESPECIAL,
                ],
            )
            .aggregate(total=Sum("quintales"))
        )["total"]

        return self._decimal_2(total or Decimal("0.00"))

    def _calcular_snapshot(self, cierre):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    kilos_reparto_directos,
                    unidades_reparto,
                    kilos_equivalentes,
                    kilos_totales,
                    quintales_cocidos,
                    rinde
                FROM fn_calcular_rinde_turno(%s, %s)
                """,
                [
                    cierre.id_jornada_id,
                    cierre.id_turno_id,
                ],
            )

            resultado = cursor.fetchone()

        quintales_cierre = self._decimal_2(cierre.quintales_cocidos or Decimal("0.00"))

        if resultado is None:
            kilos_directos = Decimal("0.00")
            unidades_totales = Decimal("0.00")
            kilos_equivalentes = Decimal("0.00")
            kilos_totales = Decimal("0.00")
        else:
            kilos_directos = self._decimal_2(resultado[0] or Decimal("0.00"))
            unidades_totales = self._decimal_2(resultado[1] or Decimal("0.00"))
            kilos_equivalentes = self._decimal_2(resultado[2] or Decimal("0.00"))
            kilos_totales = self._decimal_2(resultado[3] or Decimal("0.00"))

        if quintales_cierre > 0:
            rinde = self._decimal_4(kilos_totales / quintales_cierre)
        else:
            rinde = Decimal("0.0000")

        return {
            "quintales_cocidos": quintales_cierre,
            "kilos_directos": kilos_directos,
            "unidades_totales": unidades_totales,
            "kilos_equivalentes": kilos_equivalentes,
            "kilos_totales": kilos_totales,
            "rinde": rinde,
        }

    def update(self, request, *args, **kwargs):
        cierre = self.get_object()

        if cierre.estado == "CERRADO":
            return self._respuesta_cierre_bloqueado()

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        cierre = self.get_object()

        if cierre.estado == "CERRADO":
            return self._respuesta_cierre_bloqueado()

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        cierre = self.get_object()

        if cierre.estado == "CERRADO":
            return self._respuesta_cierre_bloqueado()

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def vista_previa(self, request, pk=None):
        cierre = self.get_object()
        snapshot = self._calcular_snapshot(cierre)

        respuesta = {
            "id_cierre_turno": cierre.id_cierre_turno,
            "estado": cierre.estado,
            "jornada_fecha": cierre.id_jornada.fecha,
            "turno_nombre": cierre.id_turno.nombre_turno,
            "mostrador_kg": cierre.mostrador_kg,
            "raciones_kg": cierre.raciones_kg,
            "ajuste_por_error_kg": cierre.ajuste_por_error_kg,
            "pan_especial_kg": cierre.pan_especial_kg,
            "detalle_pan_especial": cierre.detalle_pan_especial,
            "observacion": cierre.observacion,
            **snapshot,
        }

        return Response(respuesta)

    @action(detail=True, methods=["post"])
    def cerrar(self, request, pk=None):
        cierre = self.get_object()

        if cierre.estado == "CERRADO":
            return Response(
                {"detail": "El cierre ya se encuentra cerrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        snapshot = self._calcular_snapshot(cierre)

        cierre.quintales_cocidos = snapshot["quintales_cocidos"]
        cierre.kilos_directos = snapshot["kilos_directos"]
        cierre.unidades_totales = snapshot["unidades_totales"]
        cierre.kilos_equivalentes = snapshot["kilos_equivalentes"]
        cierre.kilos_totales = snapshot["kilos_totales"]
        cierre.rinde = snapshot["rinde"]
        cierre.estado = "CERRADO"
        cierre.fecha_cierre = timezone.now()

        cierre.full_clean()
        cierre.save()

        serializer = self.get_serializer(cierre)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reabrir(self, request, pk=None):
        cierre = self.get_object()

        if not self._usuario_es_admin(request):
            return Response(
                {"detail": "Solo el Administrador puede reabrir un cierre."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if cierre.estado != "CERRADO":
            return Response(
                {"detail": "Solo se pueden reabrir cierres en estado CERRADO."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cierre.estado = "EN_PROCESO"
        cierre.fecha_cierre = None
        cierre.save(update_fields=["estado", "fecha_cierre"])

        serializer = self.get_serializer(cierre)
        return Response(serializer.data)


# =========================================================
# BODEGA
# =========================================================

class MovimientoBodegaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoBodega.objects.all()
    serializer_class = MovimientoBodegaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class ConteoBodegaViewSet(viewsets.ModelViewSet):
    queryset = ConteoBodega.objects.all()
    serializer_class = ConteoBodegaSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


# =========================================================
# CLIENTES / PEDIDOS / MOVIMIENTOS COMERCIALES
# =========================================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_ADMIN

    @action(detail=True, methods=["get"])
    def saldo(self, request, pk=None):
        self.roles_permitidos = ROLES_ADMIN
        if not EstaAutenticadoYConRol().has_permission(request, self):
            return Response(
                {"detail": "No tiene permisos para acceder a este módulo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cliente = self.get_object()

        saldo_acumulado_obj = (
            SaldoAcumuladoCliente.objects
            .filter(id_cliente=cliente.id_cliente)
            .first()
        )

        resumen = (
            ResumenClienteDia.objects
            .filter(id_cliente=cliente.id_cliente)
            .aggregate(
                total_venta=Sum("venta_dia"),
                total_pago=Sum("pago_dia"),
            )
        )

        total_venta = resumen["total_venta"] or Decimal("0.00")
        total_pago = resumen["total_pago"] or Decimal("0.00")
        saldo_acumulado = (
            saldo_acumulado_obj.saldo_acumulado
            if saldo_acumulado_obj
            else Decimal("0.00")
        )

        return Response({
            "cliente_id": cliente.id_cliente,
            "cliente_nombre": cliente.nombre_cliente,
            "total_venta": total_venta,
            "total_pago": total_pago,
            "saldo_acumulado": saldo_acumulado,
        })


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION

    def _obtener_o_crear_jornada_pedido(self, pedido):
        fecha_jornada = pedido.fecha_entrega_solicitada or pedido.fecha_pedido
        jornada, creada = JornadaDiaria.objects.get_or_create(fecha=fecha_jornada)
        return jornada, creada

    @action(detail=True, methods=["post"], url_path="generar-movimientos")
    def generar_movimientos(self, request, pk=None):
        pedido = self.get_object()

        with transaction.atomic():
            movimientos_existentes = (
                DetalleMovimiento.objects
                .select_for_update()
                .filter(id_pedido=pedido)
                .order_by("id_detalle")
            )

            if movimientos_existentes.exists():
                serializer = DetalleMovimientoSerializer(
                    movimientos_existentes,
                    many=True
                )

                return Response(
                    {
                        "detail": "El pedido ya tiene movimientos de venta asociados. No se generaron duplicados.",
                        "pedido_id": pedido.id_pedido,
                        "movimientos_creados": 0,
                        "jornada_creada": False,
                        "movimientos": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            detalles = list(
                pedido.detalles
                .select_related("id_producto")
                .all()
            )

            if not detalles:
                return Response(
                    {
                        "detail": "El pedido no tiene detalles registrados. No se pueden generar movimientos."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            jornada, jornada_creada = self._obtener_o_crear_jornada_pedido(pedido)
            movimientos_creados = []

            for detalle in detalles:
                movimiento = DetalleMovimiento.objects.create(
                    id_jornada_id=jornada.id_jornada,
                    id_turno=None,
                    id_cliente_id=pedido.id_cliente_id,
                    id_distribucion_id=pedido.id_distribucion_id,
                    id_producto_id=detalle.id_producto_id,
                    id_pedido_id=pedido.id_pedido,
                    precio_cobrado=detalle.precio_cobrado,
                    descuento_porcentaje_aplicado=(
                        detalle.descuento_porcentaje_aplicado
                        if detalle.descuento_porcentaje_aplicado is not None
                        else Decimal("0.00")
                    ),
                    cantidad_entregada=detalle.cantidad_solicitada,
                    unidad_medida=detalle.unidad_medida,
                    cancelacion=Decimal("0.00"),
                )

                movimientos_creados.append(movimiento)

            serializer = DetalleMovimientoSerializer(
                movimientos_creados,
                many=True
            )

            return Response(
                {
                    "detail": "Movimientos de venta generados correctamente desde el pedido.",
                    "pedido_id": pedido.id_pedido,
                    "movimientos_creados": len(movimientos_creados),
                    "jornada_id": jornada.id_jornada,
                    "jornada_fecha": jornada.fecha,
                    "jornada_creada": jornada_creada,
                    "movimientos": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION



class DetalleRepartoTurnoViewSet(viewsets.ModelViewSet):
    queryset = (
        DetalleRepartoTurno.objects
        .select_related("id_jornada", "id_turno", "id_cliente", "id_distribucion")
        .all()
    )
    serializer_class = DetalleRepartoTurnoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION


class DetalleMovimientoViewSet(viewsets.ModelViewSet):
    queryset = DetalleMovimiento.objects.all()
    serializer_class = DetalleMovimientoSerializer
    permission_classes = [IsAuthenticated, EstaAutenticadoLecturaORolEscritura]
    roles_escritura = ROLES_OPERACION

    @action(detail=False, methods=["get"])
    def resumen_jornada(self, request):
        self.roles_permitidos = ROLES_ADMIN

        if not EstaAutenticadoYConRol().has_permission(request, self):
            return Response(
                {"detail": "No tiene permisos para acceder a este módulo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        jornada_id = request.query_params.get("jornada_id")

        if not jornada_id:
            return Response(
                {"error": "jornada_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            jornada = JornadaDiaria.objects.get(id_jornada=jornada_id)
        except JornadaDiaria.DoesNotExist:
            return Response(
                {"error": "Jornada no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        resumen = (
            ResumenClienteDia.objects
            .filter(fecha=jornada.fecha)
            .values(
                "id_cliente",
                "nombre_cliente",
                "venta_dia",
                "pago_dia",
                "saldo_dia",
            )
        )

        respuesta = []

        for item in resumen:
            respuesta.append({
                "id_cliente": item["id_cliente"],
                "cliente_nombre": item["nombre_cliente"],
                "total_venta": item["venta_dia"],
                "total_pago": item["pago_dia"],
                "saldo_dia": item["saldo_dia"],
            })

        return Response(respuesta)


# =========================================================
# REPORTES
# =========================================================

class ReportesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, EstaAutenticadoYConRol]
    roles_permitidos = ROLES_ADMIN

    @action(detail=False, methods=["get"])
    def stock_insumo(self, request):
        insumo_id = request.query_params.get("insumo_id")
        fecha_param = request.query_params.get("fecha")

        if not insumo_id:
            return Response(
                {"error": "insumo_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fecha_consulta = date.today()

        if fecha_param:
            fecha_parseada = parse_date(fecha_param)

            if not fecha_parseada:
                return Response(
                    {"error": "fecha debe tener formato YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fecha_consulta = fecha_parseada

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT fn_stock_insumo_fecha(%s, %s)",
                [insumo_id, fecha_consulta],
            )
            stock_teorico = cursor.fetchone()[0]

        ultimo_conteo = (
            ConteoBodega.objects
            .filter(id_insumo_id=insumo_id)
            .order_by("-fecha_conteo")
            .first()
        )

        cantidad_fisica = ultimo_conteo.cantidad_fisica if ultimo_conteo else None

        diferencia = None
        if cantidad_fisica is not None:
            diferencia = stock_teorico - cantidad_fisica

        return Response({
            "insumo_id": insumo_id,
            "fecha_consulta": fecha_consulta,
            "stock_teorico": stock_teorico,
            "ultimo_conteo": cantidad_fisica,
            "fecha_ultimo_conteo": ultimo_conteo.fecha_conteo if ultimo_conteo else None,
            "diferencia": diferencia,
        })


# =========================================================
# USUARIO AUTENTICADO
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def usuario_actual(request):
    usuario = request.user

    roles = list(
        usuario.groups.values_list("name", flat=True)
    )

    return Response({
        "id": usuario.id,
        "username": usuario.username,
        "is_superuser": usuario.is_superuser,
        "roles": roles,
    })


# =========================================================
# 2FA - DOBLE FACTOR DE AUTENTICACIÓN
# =========================================================

from .serializers import TwoFactorLoginSerializer, TwoFactorVerifySerializer
from .models import TwoFactorCode
from .email_utils import enviar_codigo_2fa
from datetime import timedelta


@api_view(["POST"])
@permission_classes([AllowAny])
def two_factor_obtain(request):
    serializer = TwoFactorLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )

    if user is None:
        return Response(
            {"error": "Credenciales incorrectas"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"error": "Usuario inactivo"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    TwoFactorCode.objects.filter(user=user, is_used=False).update(is_used=True)

    codigo = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(
        minutes=settings.TWO_FACTOR_CODE_EXPIRY_MINUTES
    )

    tf_code = TwoFactorCode.objects.create(
        user=user, code=codigo, expires_at=expires_at
    )

    if user.email:
        try:
            enviar_codigo_2fa(user.email, codigo, user.username)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando 2FA a {user.email}: {e}")

    return Response(
        {
            "session_id": str(tf_code.session_id),
            "message": f"Código enviado a {user.email}",
            "expires_in": settings.TWO_FACTOR_CODE_EXPIRY_MINUTES * 60,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def two_factor_verify(request):
    serializer = TwoFactorVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        tf_code = TwoFactorCode.objects.get(
            session_id=serializer.validated_data["session_id"],
            code=serializer.validated_data["code"],
            is_used=False,
        )
    except TwoFactorCode.DoesNotExist:
        return Response(
            {"error": "Código inválido o expirado"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not tf_code.is_valid():
        return Response(
            {"error": "Código expirado. Solicite uno nuevo."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    tf_code.mark_as_used()

    refresh = RefreshToken.for_user(tf_code.user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "healthy"})