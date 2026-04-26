from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_funcion_rinde_trigger_cierre"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION fn_calcular_rinde_turno(
                p_id_jornada BIGINT,
                p_id_turno INTEGER
            )
            RETURNS TABLE (
                id_jornada BIGINT,
                id_turno INTEGER,
                kilos_reparto_directos NUMERIC(14,4),
                unidades_reparto NUMERIC(14,4),
                kilos_equivalentes NUMERIC(14,4),
                mostrador_kg NUMERIC(14,4),
                pan_especial_kg NUMERIC(14,4),
                raciones_kg NUMERIC(14,4),
                ajuste_por_error_kg NUMERIC(14,4),
                kilos_totales NUMERIC(14,4),
                quintales_cocidos NUMERIC(14,4),
                rinde NUMERIC(14,4)
            )
            LANGUAGE plpgsql
            AS $$
            BEGIN
                IF p_id_jornada IS NULL THEN
                    RAISE EXCEPTION 'El parámetro p_id_jornada no puede ser NULL';
                END IF;

                IF p_id_turno IS NULL THEN
                    RAISE EXCEPTION 'El parámetro p_id_turno no puede ser NULL';
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM jornada_diaria jd
                    WHERE jd.id_jornada = p_id_jornada
                ) THEN
                    RAISE EXCEPTION 'No existe la jornada con id_jornada = %', p_id_jornada;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM turno t
                    WHERE t.id_turno = p_id_turno
                ) THEN
                    RAISE EXCEPTION 'No existe el turno con id_turno = %', p_id_turno;
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM cierre_turno ct
                    WHERE ct.id_jornada = p_id_jornada
                    AND ct.id_turno = p_id_turno
                ) THEN
                    RAISE EXCEPTION 'No existe cierre_turno para id_jornada = % e id_turno = %',
                        p_id_jornada, p_id_turno;
                END IF;

                RETURN QUERY
                WITH movimientos AS (
                    SELECT
                        ROUND(
                            COALESCE(SUM(
                                CASE
                                    WHEN dm.unidad_medida = 'KILO'
                                    THEN dm.cantidad_entregada
                                    ELSE 0
                                END
                            ), 0),
                            2
                        ) AS kilos_directos_calc,
                        ROUND(
                            COALESCE(SUM(
                                CASE
                                    WHEN dm.unidad_medida = 'UNIDAD'
                                    THEN dm.cantidad_entregada
                                    ELSE 0
                                END
                            ), 0),
                            2
                        ) AS unidades_calc
                    FROM detalle_movimiento dm
                    JOIN producto p
                        ON p.id_producto = dm.id_producto
                    JOIN tipo_produccion tp
                        ON tp.id_tipo_produccion = p.id_tipo_produccion
                    WHERE dm.id_jornada = p_id_jornada
                    AND dm.id_turno = p_id_turno
                    AND tp.nombre_tipo_produccion = 'Pan corriente'
                ),
                quintales AS (
                    SELECT
                        ROUND(COALESCE(SUM(pr.quintales), 0), 2) AS quintales_cocidos_calc
                    FROM produccion pr
                    JOIN tipo_produccion tp
                        ON tp.id_tipo_produccion = pr.id_tipo_produccion
                    WHERE pr.id_jornada = p_id_jornada
                    AND pr.id_turno = p_id_turno
                    AND tp.nombre_tipo_produccion IN ('Pan corriente', 'Pan especial')
                ),
                cierre AS (
                    SELECT
                        COALESCE(ct.mostrador_kg, 0) AS mostrador_kg_calc,
                        COALESCE(ct.pan_especial_kg, 0) AS pan_especial_kg_calc,
                        COALESCE(ct.raciones_kg, 0) AS raciones_kg_calc,
                        COALESCE(ct.ajuste_por_error_kg, 0) AS ajuste_por_error_kg_calc
                    FROM cierre_turno ct
                    WHERE ct.id_jornada = p_id_jornada
                    AND ct.id_turno = p_id_turno
                ),
                calculo AS (
                    SELECT
                        p_id_jornada AS jornada_calc,
                        p_id_turno AS turno_calc,
                        m.kilos_directos_calc,
                        m.unidades_calc,
                        ROUND(m.unidades_calc / 13, 2) AS kilos_equivalentes_calc,
                        c.mostrador_kg_calc,
                        c.pan_especial_kg_calc,
                        c.raciones_kg_calc,
                        c.ajuste_por_error_kg_calc,
                        q.quintales_cocidos_calc
                    FROM movimientos m
                    CROSS JOIN quintales q
                    CROSS JOIN cierre c
                ),
                resultado AS (
                    SELECT
                        calc.jornada_calc,
                        calc.turno_calc,
                        calc.kilos_directos_calc,
                        calc.unidades_calc,
                        calc.kilos_equivalentes_calc,
                        calc.mostrador_kg_calc,
                        calc.pan_especial_kg_calc,
                        calc.raciones_kg_calc,
                        calc.ajuste_por_error_kg_calc,
                        ROUND(
                            calc.kilos_directos_calc
                            + calc.kilos_equivalentes_calc
                            + calc.mostrador_kg_calc
                            + calc.pan_especial_kg_calc
                            + calc.raciones_kg_calc
                            + calc.ajuste_por_error_kg_calc,
                            2
                        ) AS kilos_totales_calc,
                        calc.quintales_cocidos_calc
                    FROM calculo calc
                )
                SELECT
                    r.jornada_calc::BIGINT,
                    r.turno_calc::INTEGER,
                    r.kilos_directos_calc::NUMERIC(14,4),
                    r.unidades_calc::NUMERIC(14,4),
                    r.kilos_equivalentes_calc::NUMERIC(14,4),
                    r.mostrador_kg_calc::NUMERIC(14,4),
                    r.pan_especial_kg_calc::NUMERIC(14,4),
                    r.raciones_kg_calc::NUMERIC(14,4),
                    r.ajuste_por_error_kg_calc::NUMERIC(14,4),
                    r.kilos_totales_calc::NUMERIC(14,4),
                    r.quintales_cocidos_calc::NUMERIC(14,4),
                    (
                        CASE
                            WHEN r.quintales_cocidos_calc > 0
                            THEN ROUND(r.kilos_totales_calc / r.quintales_cocidos_calc, 4)
                            ELSE 0
                        END
                    )::NUMERIC(14,4)
                FROM resultado r;
            END;
            $$;
            """,
        ),
    ]