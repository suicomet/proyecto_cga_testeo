from django.core.management.base import BaseCommand
from api.models import Turno, Distribucion

class Command(BaseCommand):
    help = 'Carga datos iniciales de Turno y Distribución según especificación del proyecto'
    
    def handle(self, *args, **options):
        # Datos para Turno
        turnos_data = [
            {'id_turno': 1, 'nombre_turno': 'Noche'},
            {'id_turno': 2, 'nombre_turno': 'Mañana'},
            {'id_turno': 3, 'nombre_turno': 'Tarde'},
        ]
        
        for turno_data in turnos_data:
            turno, created = Turno.objects.update_or_create(
                id_turno=turno_data['id_turno'],
                defaults={'nombre_turno': turno_data['nombre_turno']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Turno creado: {turno.nombre_turno}'))
            else:
                self.stdout.write(self.style.WARNING(f'Turno actualizado: {turno.nombre_turno}'))
        
        # Datos para Distribución
        distribuciones_data = [
            {'id_distribucion': 1, 'nombre_distribucion': 'Repartidor 1'},
            {'id_distribucion': 2, 'nombre_distribucion': 'Repartidor 2'},
            {'id_distribucion': 3, 'nombre_distribucion': 'Retiro en panadería'},
            {'id_distribucion': 4, 'nombre_distribucion': 'Sala de ventas'},
        ]
        
        for dist_data in distribuciones_data:
            distribucion, created = Distribucion.objects.update_or_create(
                id_distribucion=dist_data['id_distribucion'],
                defaults={'nombre_distribucion': dist_data['nombre_distribucion']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Distribución creada: {distribucion.nombre_distribucion}'))
            else:
                self.stdout.write(self.style.WARNING(f'Distribución actualizada: {distribucion.nombre_distribucion}'))
        
        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados exitosamente'))