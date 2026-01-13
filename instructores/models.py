from django.db import models
from django.contrib.auth.models import User

class Instructor(models.Model):
    # Relación 1 a 1 con el Usuario (Login)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    cedula = models.CharField(max_length=20, unique=True)
    profesion = models.CharField(max_length=100)
    tipo_contrato = models.CharField(
        max_length=50, 
        choices=[('PLANTA', 'Planta'), ('CONTRATISTA', 'Contratista')]
    )
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - {self.profesion}"