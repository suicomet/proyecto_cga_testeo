import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    nombre_turno = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_turno

    class Meta:
        db_table = "turno"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre_turno"],
                name="unique_turno_nombre",
            )
        ]


class Distribucion(models.Model):
    id_distribucion = models.AutoField(primary_key=True)
    nombre_distribucion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_distribucion

    class Meta:
        db_table = "distribucion"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre_distribucion"],
                name="unique_distribucion_nombre",
            )
        ]


class Insumo(models.Model):
    id_insumo = models.AutoField(primary_key=True)
    nombre_insumo = models.CharField(max_length=200)
    unidad_control = models.CharField(max_length=20)
    stock_sugerido_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.CharField(max_length=1, default="S")

    def __str__(self):
        return self.nombre_insumo

    class Meta:
        db_table = "insumo"
        constraints = [
            models.CheckConstraint(
                check=models.Q(activo__in=["S", "N"]),
                name="check_insumo_activo",
            )
        ]


class TipoProduccion(models.Model):
    id_tipo_produccion = models.AutoField(primary_key=True)
    nombre_tipo_produccion = models.CharField(max_length=200)
    id_insumo_principal = models.ForeignKey(
        Insumo,
        on_delete=models.SET_NULL,
        null=True,
        db_column="id_insumo_principal",
    )

    def __str__(self):
        return self.nombre_tipo_produccion

    class Meta:
        db_table = "tipo_produccion"


class JornadaDiaria(models.Model):
    id_jornada = models.AutoField(primary_key=True)
    fecha = models.DateField(unique=True)

    def __str__(self):
        return f"Jornada {self.fecha}"

    class Meta:
        db_table = "jornada_diaria"


class Produccion(models.Model):
    id_produccion = models.AutoField(primary_key=True)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.CASCADE,
        db_column="id_jornada",
    )
    id_tipo_produccion = models.ForeignKey(
        TipoProduccion,
        on_delete=models.CASCADE,
        db_column="id_tipo_produccion",
    )
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        db_column="id_turno",
    )
    quintales = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Producción {self.id_tipo_produccion} - {self.id_jornada.fecha}"

    class Meta:
        db_table = "produccion"
        unique_together = ("id_jornada", "id_tipo_produccion", "id_turno")
        indexes = [
            models.Index(fields=["id_jornada"], name="idx_prod_jornada"),
        ]


class CierreTurno(models.Model):
    ESTADO_CHOICES = [
        ("EN_PROCESO", "En proceso"),
        ("CERRADO", "Cerrado"),
    ]

    id_cierre_turno = models.AutoField(primary_key=True)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.CASCADE,
        db_column="id_jornada",
    )
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        db_column="id_turno",
    )
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default="EN_PROCESO",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    mostrador_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    raciones_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    ajuste_por_error_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    pan_especial_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    detalle_pan_especial = models.TextField(null=True, blank=True)
    observacion = models.TextField(null=True, blank=True)

    quintales_cocidos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    kilos_directos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    unidades_totales = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    kilos_equivalentes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    kilos_totales = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    rinde = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"Cierre {self.id_jornada.fecha} - {self.id_turno.nombre_turno}"

    def clean(self):
        if self.ajuste_por_error_kg != 0 and not self.observacion:
            raise ValidationError({
                "observacion": "La observación es obligatoria cuando existe ajuste por error."
            })

    class Meta:
        db_table = "cierre_turno"
        indexes = [
            models.Index(fields=["id_jornada"], name="idx_ct_jornada"),
            models.Index(fields=["id_turno"], name="idx_ct_turno"),
            models.Index(fields=["estado"], name="idx_ct_estado"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["id_jornada", "id_turno"],
                name="unique_cierre_turno_jornada_turno",
            ),
            models.CheckConstraint(
                check=models.Q(estado__in=["EN_PROCESO", "CERRADO"]),
                name="check_cierre_turno_estado",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(ajuste_por_error_kg=0)
                    | (
                        models.Q(observacion__isnull=False)
                        & ~models.Q(observacion="")
                    )
                ),
                name="check_cierre_turno_ajuste_observacion",
            ),
        ]


class MovimientoBodega(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
        ("AJUSTE", "Ajuste"),
    ]

    id_movimiento_bodega = models.AutoField(primary_key=True)
    id_insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        db_column="id_insumo",
    )
    fecha_movimiento = models.DateField()
    tipo_movimiento = models.CharField(
        max_length=10,
        choices=TIPO_MOVIMIENTO_CHOICES,
    )
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_jornada",
    )
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_turno",
    )

    def __str__(self):
        return f"{self.tipo_movimiento} {self.id_insumo} - {self.fecha_movimiento}"

    class Meta:
        db_table = "movimiento_bodega"
        constraints = [
            models.CheckConstraint(
                check=models.Q(tipo_movimiento__in=["ENTRADA", "SALIDA", "AJUSTE"]),
                name="check_tipo_movimiento",
            )
        ]


class ConteoBodega(models.Model):
    id_conteo_bodega = models.AutoField(primary_key=True)
    id_insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        db_column="id_insumo",
    )
    fecha_conteo = models.DateField()
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_turno",
    )
    cantidad_fisica = models.DecimalField(max_digits=10, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Conteo {self.id_insumo} - {self.fecha_conteo}"

    class Meta:
        db_table = "conteo_bodega"
        unique_together = ("id_insumo", "fecha_conteo", "id_turno")


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    rut = models.IntegerField(validators=[MinValueValidator(0)])
    digito_verificador = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    descuento_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.nombre_cliente

    class Meta:
        db_table = "cliente"
        constraints = [
            models.UniqueConstraint(
                fields=["rut", "digito_verificador"],
                name="unique_cliente_rut_dv",
            )
        ]


class Producto(models.Model):
    UNIDAD_VENTA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
        ("AMBOS", "Ambos"),
    ]

    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=200)
    precio_sugerido = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_venta_base = models.CharField(
        max_length=10,
        choices=UNIDAD_VENTA_CHOICES,
        default="KILO",
    )
    id_tipo_produccion = models.ForeignKey(
        TipoProduccion,
        on_delete=models.SET_NULL,
        null=True,
        db_column="id_tipo_produccion",
    )

    def __str__(self):
        return self.nombre_producto

    class Meta:
        db_table = "producto"
        constraints = [
            models.CheckConstraint(
                check=models.Q(unidad_venta_base__in=["KILO", "UNIDAD", "AMBOS"]),
                name="check_producto_unidad_venta_base",
            )
        ]


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column="id_cliente",
    )
    id_distribucion = models.ForeignKey(
        Distribucion,
        on_delete=models.CASCADE,
        db_column="id_distribucion",
    )
    fecha_pedido = models.DateField()
    fecha_entrega_solicitada = models.DateField()

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.id_cliente}"

    class Meta:
        db_table = "pedido"
        indexes = [
            models.Index(fields=["id_cliente"], name="idx_pedido_cliente"),
        ]


class DetallePedido(models.Model):
    UNIDAD_MEDIDA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
    ]

    id_detalle_pedido = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column="id_pedido",
        related_name="detalles",
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column="id_producto",
    )
    cantidad_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA_CHOICES,
        default="KILO",
    )
    precio_cobrado = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_porcentaje_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Detalle {self.id_producto} - Pedido {self.id_pedido}"

    class Meta:
        db_table = "detalle_pedido"
        indexes = [
            models.Index(fields=["id_pedido"], name="idx_dp_pedido"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(descuento_porcentaje_aplicado__gte=0)
                    & models.Q(descuento_porcentaje_aplicado__lte=100)
                ),
                name="check_descuento_detalle_pedido",
            ),
            models.CheckConstraint(
                check=models.Q(unidad_medida__in=["KILO", "UNIDAD"]),
                name="check_detalle_pedido_unidad_medida",
            ),
        ]


class DetalleMovimiento(models.Model):
    UNIDAD_MEDIDA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
    ]

    id_detalle = models.AutoField(primary_key=True)
    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.CASCADE,
        db_column="id_jornada",
    )
    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_turno",
    )
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column="id_cliente",
    )
    id_distribucion = models.ForeignKey(
        Distribucion,
        on_delete=models.CASCADE,
        db_column="id_distribucion",
    )
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column="id_producto",
    )
    id_pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="id_pedido",
    )
    precio_cobrado = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_porcentaje_aplicado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    cantidad_entregada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA_CHOICES,
        default="KILO",
    )
    cancelacion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        turno = self.id_turno.nombre_turno if self.id_turno else "Sin turno"
        return f"Movimiento {self.id_cliente} - {self.id_jornada.fecha} - {turno}"

    @property
    def venta_linea(self):
        return self.precio_cobrado * self.cantidad_entregada

    class Meta:
        db_table = "detalle_movimiento"
        indexes = [
            models.Index(fields=["id_cliente"], name="idx_dm_cliente"),
            models.Index(fields=["id_jornada"], name="idx_dm_jornada"),
            models.Index(fields=["id_turno"], name="idx_dm_turno"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(descuento_porcentaje_aplicado__gte=0)
                    & models.Q(descuento_porcentaje_aplicado__lte=100)
                ),
                name="check_descuento_detalle_movimiento",
            ),
            models.CheckConstraint(
                check=models.Q(unidad_medida__in=["KILO", "UNIDAD"]),
                name="check_detalle_movimiento_unidad_medida",
            ),
        ]


class ResumenClienteDia(models.Model):
    id = models.BigIntegerField(primary_key=True)
    fecha = models.DateField()
    id_cliente = models.BigIntegerField()
    rut = models.IntegerField()
    digito_verificador = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=150)
    venta_dia = models.DecimalField(max_digits=20, decimal_places=2)
    pago_dia = models.DecimalField(max_digits=20, decimal_places=2)
    saldo_dia = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        managed = False
        db_table = "vw_resumen_cliente_dia"


class SaldoAcumuladoCliente(models.Model):
    id = models.BigIntegerField(primary_key=True)
    id_cliente = models.BigIntegerField()
    rut = models.IntegerField()
    digito_verificador = models.CharField(max_length=1)
    nombre_cliente = models.CharField(max_length=150)
    saldo_acumulado = models.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        managed = False
        db_table = "vw_saldo_acumulado_cliente"


class TwoFactorCode(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "two_factor_code"

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])


class DetalleRepartoTurno(models.Model):
    UNIDAD_MEDIDA_CHOICES = [
        ("KILO", "Kilo"),
        ("UNIDAD", "Unidad"),
    ]

    id_detalle_reparto_turno = models.AutoField(primary_key=True)

    id_jornada = models.ForeignKey(
        JornadaDiaria,
        on_delete=models.CASCADE,
        db_column="id_jornada",
    )

    id_turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        db_column="id_turno",
    )

    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        db_column="id_cliente",
    )

    id_distribucion = models.ForeignKey(
        Distribucion,
        on_delete=models.CASCADE,
        db_column="id_distribucion",
    )

    cantidad_entregada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    unidad_medida = models.CharField(
        max_length=10,
        choices=UNIDAD_MEDIDA_CHOICES,
        default="KILO",
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    observacion = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"Reparto {self.id_cliente} - "
            f"{self.id_jornada.fecha} - "
            f"{self.id_turno.nombre_turno}"
        )

    class Meta:
        db_table = "detalle_reparto_turno"
        indexes = [
            models.Index(fields=["id_jornada"], name="idx_drt_jornada"),
            models.Index(fields=["id_turno"], name="idx_drt_turno"),
            models.Index(fields=["id_cliente"], name="idx_drt_cliente"),
            models.Index(fields=["id_distribucion"], name="idx_drt_distribucion"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(unidad_medida__in=["KILO", "UNIDAD"]),
                name="check_drt_unidad_medida",
            ),
            models.CheckConstraint(
                check=models.Q(cantidad_entregada__gte=0),
                name="check_drt_cantidad_no_negativa",
            ),
        ]
