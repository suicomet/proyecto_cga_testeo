from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import (
    Turno, Distribucion, Insumo, TipoProduccion, JornadaDiaria, Produccion,
    MovimientoBodega, ConteoBodega, Cliente, Producto, Pedido, DetallePedido,
    DetalleMovimiento
)
from decimal import Decimal
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Crea datos de prueba realistas para el sistema de panadería'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creando datos de prueba...'))
        
        # 1. Crear insumos básicos
        insumos_data = [
            {'nombre_insumo': 'Harina', 'unidad_control': 'kg', 'stock_sugerido_inicial': 1000, 'activo': 'S'},
            {'nombre_insumo': 'Azúcar', 'unidad_control': 'kg', 'stock_sugerido_inicial': 200, 'activo': 'S'},
            {'nombre_insumo': 'Levadura', 'unidad_control': 'kg', 'stock_sugerido_inicial': 50, 'activo': 'S'},
            {'nombre_insumo': 'Sal', 'unidad_control': 'kg', 'stock_sugerido_inicial': 100, 'activo': 'S'},
            {'nombre_insumo': 'Manteca', 'unidad_control': 'kg', 'stock_sugerido_inicial': 150, 'activo': 'S'},
            {'nombre_insumo': 'Huevos', 'unidad_control': 'unidad', 'stock_sugerido_inicial': 500, 'activo': 'S'},
        ]
        
        insumos = []
        for i, data in enumerate(insumos_data, 1):
            insumo, created = Insumo.objects.update_or_create(
                id_insumo=i,
                defaults=data
            )
            insumos.append(insumo)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Insumo creado: {insumo.nombre_insumo}'))
        
        # 2. Crear tipos de producción
        tipos_produccion_data = [
            {'nombre_tipo_produccion': 'Pan corriente', 'id_insumo_principal': insumos[0]},  # Harina
            {'nombre_tipo_produccion': 'Pan integral', 'id_insumo_principal': insumos[0]},   # Harina
            {'nombre_tipo_produccion': 'Pan dulce', 'id_insumo_principal': insumos[0]},      # Harina
            {'nombre_tipo_produccion': 'Facturas', 'id_insumo_principal': insumos[0]},       # Harina
            {'nombre_tipo_produccion': 'Tortas', 'id_insumo_principal': insumos[0]},         # Harina
        ]
        
        tipos_produccion = []
        for i, data in enumerate(tipos_produccion_data, 1):
            tipo, created = TipoProduccion.objects.update_or_create(
                id_tipo_produccion=i,
                defaults=data
            )
            tipos_produccion.append(tipo)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Tipo producción creado: {tipo.nombre_tipo_produccion}'))
        
        # 3. Crear productos comerciales
        productos_data = [
            {'nombre_producto': 'Pan corriente 1kg', 'precio_sugerido': 2500, 'id_tipo_produccion': tipos_produccion[0]},
            {'nombre_producto': 'Pan corriente 500g', 'precio_sugerido': 1300, 'id_tipo_produccion': tipos_produccion[0]},
            {'nombre_producto': 'Pan integral 1kg', 'precio_sugerido': 3200, 'id_tipo_produccion': tipos_produccion[1]},
            {'nombre_producto': 'Medialunas', 'precio_sugerido': 300, 'id_tipo_produccion': tipos_produccion[3]},
            {'nombre_producto': 'Facturas surtidas', 'precio_sugerido': 2800, 'id_tipo_produccion': tipos_produccion[3]},
            {'nombre_producto': 'Torta chocolate', 'precio_sugerido': 12000, 'id_tipo_produccion': tipos_produccion[4]},
            {'nombre_producto': 'Torta vainilla', 'precio_sugerido': 11000, 'id_tipo_produccion': tipos_produccion[4]},
        ]
        
        productos = []
        for i, data in enumerate(productos_data, 1):
            producto, created = Producto.objects.update_or_create(
                id_producto=i,
                defaults=data
            )
            productos.append(producto)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Producto creado: {producto.nombre_producto} - ${producto.precio_sugerido}'))
        
        # 4. Crear clientes
        clientes_data = [
            {'rut': '12345678', 'digito_verificador': '9', 'nombre_cliente': 'Supermercado Los Andes', 'ciudad': 'Santiago', 'direccion': 'Av. Principal 123', 'telefono': '+56912345678', 'descuento_aplicado': 5},
            {'rut': '87654321', 'digito_verificador': '0', 'nombre_cliente': 'Restaurante La Familia', 'ciudad': 'Santiago', 'direccion': 'Calle Secundaria 456', 'telefono': '+56987654321', 'descuento_aplicado': 10},
            {'rut': '11222333', 'digito_verificador': '4', 'nombre_cliente': 'Cafetería Central', 'ciudad': 'Santiago', 'direccion': 'Plaza Mayor 789', 'telefono': '+56911223344', 'descuento_aplicado': 8},
            {'rut': '44555666', 'digito_verificador': '7', 'nombre_cliente': 'Hotel Panorámico', 'ciudad': 'Santiago', 'direccion': 'Cerro Alegre 321', 'telefono': '+56944556677', 'descuento_aplicado': 12},
            {'rut': '77888999', 'digito_verificador': '2', 'nombre_cliente': 'Colegio San José', 'ciudad': 'Santiago', 'direccion': 'Av. Educacional 654', 'telefono': '+56977889900', 'descuento_aplicado': 15},
        ]
        
        clientes = []
        for i, data in enumerate(clientes_data, 1):
            cliente, created = Cliente.objects.update_or_create(
                id_cliente=i,
                defaults=data
            )
            clientes.append(cliente)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Cliente creado: {cliente.nombre_cliente} - Descuento: {cliente.descuento_aplicado}%'))
        
        # 5. Obtener turnos y distribuciones existentes
        turnos = list(Turno.objects.all())
        distribuciones = list(Distribucion.objects.all())
        
        # 6. Crear jornadas de los últimos 7 días
        jornadas = []
        for i in range(7):
            fecha = date.today() - timedelta(days=i)
            jornada, created = JornadaDiaria.objects.update_or_create(
                fecha=fecha,
                defaults={'fecha': fecha}
            )
            if created:
                jornadas.append(jornada)
                self.stdout.write(self.style.SUCCESS(f'Jornada creada: {fecha}'))
        
        # 7. Crear producción para cada jornada
        for jornada in jornadas:
            for tipo in tipos_produccion:
                for turno in turnos:
                    produccion, created = Produccion.objects.update_or_create(
                        id_jornada=jornada,
                        id_tipo_produccion=tipo,
                        id_turno=turno,
                        defaults={'quintales': Decimal(random.uniform(10, 50)).quantize(Decimal('0.01'))}
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Producción creada para {len(jornadas)} jornadas'))
        
        # 8. Crear movimientos de bodega
        for i in range(20):
            fecha_mov = date.today() - timedelta(days=random.randint(0, 30))
            movimiento = MovimientoBodega.objects.create(
                id_insumo=random.choice(insumos),
                fecha_movimiento=fecha_mov,
                tipo_movimiento=random.choice(['ENTRADA', 'SALIDA']),
                cantidad=Decimal(random.uniform(10, 100)).quantize(Decimal('0.01')),
                id_jornada=random.choice(jornadas) if random.random() > 0.3 else None,
                id_turno=random.choice(turnos) if random.random() > 0.3 else None
            )
        
        self.stdout.write(self.style.SUCCESS('20 movimientos de bodega creados'))
        
        # 9. Crear pedidos
        for i in range(10):
            fecha_pedido = date.today() - timedelta(days=random.randint(1, 14))
            fecha_entrega = fecha_pedido + timedelta(days=random.randint(1, 3))
            
            pedido = Pedido.objects.create(
                id_cliente=random.choice(clientes),
                id_distribucion=random.choice(distribuciones),
                fecha_pedido=fecha_pedido,
                fecha_entrega_solicitada=fecha_entrega
            )
            
            # Agregar detalles al pedido
            num_detalles = random.randint(1, 5)
            for j in range(num_detalles):
                producto = random.choice(productos)
                DetallePedido.objects.create(
                    id_pedido=pedido,
                    id_producto=producto,
                    cantidad_solicitada=Decimal(random.uniform(5, 50)).quantize(Decimal('0.01')),
                    precio_cobrado=producto.precio_sugerido * Decimal('0.95'),  # 5% descuento base
                    descuento_porcentaje_aplicado=pedido.id_cliente.descuento_aplicado
                )
        
        self.stdout.write(self.style.SUCCESS('10 pedidos con detalles creados'))
        
        # 10. Crear movimientos reales (detalle_movimiento)
        for jornada in jornadas:
            for cliente in random.sample(clientes, min(3, len(clientes))):
                for _ in range(random.randint(1, 3)):
                    producto = random.choice(productos)
                    movimiento = DetalleMovimiento.objects.create(
                        id_jornada=jornada,
                        id_cliente=cliente,
                        id_distribucion=random.choice(distribuciones),
                        id_producto=producto,
                        id_pedido=Pedido.objects.filter(id_cliente=cliente).first() if random.random() > 0.5 else None,
                        precio_cobrado=producto.precio_sugerido * Decimal(str(1 - cliente.descuento_aplicado/100)),
                        descuento_porcentaje_aplicado=cliente.descuento_aplicado,
                        kilos=Decimal(random.uniform(1, 20)).quantize(Decimal('0.01')),
                        cancelacion=Decimal(random.uniform(1000, 50000)).quantize(Decimal('0.01'))
                    )
        
        self.stdout.write(self.style.SUCCESS(f'Movimientos reales creados para {len(jornadas)} jornadas'))
        
        # 11. Crear conteos de bodega
        for insumo in insumos:
            conteo = ConteoBodega.objects.create(
                id_insumo=insumo,
                fecha_conteo=date.today() - timedelta(days=random.randint(0, 7)),
                id_turno=random.choice(turnos) if random.random() > 0.3 else None,
                cantidad_fisica=Decimal(random.uniform(50, 500)).quantize(Decimal('0.01')),
                observacion='Conteo físico rutinario' if random.random() > 0.5 else 'Ajuste por diferencia'
            )
        
        self.stdout.write(self.style.SUCCESS('Conteos de bodega creados para todos los insumos'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DATOS DE PRUEBA CREADOS EXITOSAMENTE'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'- {len(insumos)} insumos'))
        self.stdout.write(self.style.SUCCESS(f'- {len(tipos_produccion)} tipos de producción'))
        self.stdout.write(self.style.SUCCESS(f'- {len(productos)} productos comerciales'))
        self.stdout.write(self.style.SUCCESS(f'- {len(clientes)} clientes'))
        self.stdout.write(self.style.SUCCESS(f'- {len(jornadas)} jornadas diarias'))
        self.stdout.write(self.style.SUCCESS(f'- 20 movimientos de bodega'))
        self.stdout.write(self.style.SUCCESS(f'- 10 pedidos con detalles'))
        self.stdout.write(self.style.SUCCESS(f'- Movimientos reales por jornada'))
        self.stdout.write(self.style.SUCCESS(f'- Conteos de bodega para todos los insumos'))
        self.stdout.write(self.style.SUCCESS('\nBackend listo para pruebas: http://localhost:8000/api/'))
        self.stdout.write(self.style.SUCCESS('Admin: http://localhost:8000/admin (admin/admin123)'))