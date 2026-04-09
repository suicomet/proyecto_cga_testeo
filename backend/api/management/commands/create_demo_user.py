from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea un usuario demo para pruebas'
    
    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'
        email = 'admin@panaderia.local'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Usuario demo creado: {username}/{password}'))
        else:
            self.stdout.write(self.style.WARNING(f'El usuario {username} ya existe'))