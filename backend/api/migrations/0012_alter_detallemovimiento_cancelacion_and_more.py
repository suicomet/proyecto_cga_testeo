# Generated manually after QA audit: prevent financial NULL values in detalle_movimiento.

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_twofactorcode"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE detalle_movimiento
            DISABLE TRIGGER trg_bloquear_movimiento_cierre_cerrado;
            """,
            reverse_sql="""
            ALTER TABLE detalle_movimiento
            ENABLE TRIGGER trg_bloquear_movimiento_cierre_cerrado;
            """,
        ),

        migrations.AlterField(
            model_name="detallemovimiento",
            name="cancelacion",
            field=models.DecimalField(
                max_digits=12,
                decimal_places=2,
                default=0,
            ),
        ),

        migrations.AlterField(
            model_name="detallemovimiento",
            name="descuento_porcentaje_aplicado",
            field=models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0,
                validators=[
                    MinValueValidator(0),
                    MaxValueValidator(100),
                ],
            ),
        ),

        migrations.RunSQL(
            sql="""
            ALTER TABLE detalle_movimiento
            ENABLE TRIGGER trg_bloquear_movimiento_cierre_cerrado;
            """,
            reverse_sql="""
            ALTER TABLE detalle_movimiento
            DISABLE TRIGGER trg_bloquear_movimiento_cierre_cerrado;
            """,
        ),
    ]
