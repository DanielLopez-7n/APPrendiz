from django.db import models
from django.contrib.auth.models import User

class Instructor(models.Model):
    # Relación 1 a 1 con el Usuario
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    profesion = models.CharField(max_length=100, verbose_name="Profesión / Especialidad")
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Celular")
    
    # Mantenemos esto por si quieres filtrar por tipo
    tipo_contrato = models.CharField(
        max_length=50, 
        choices=[('PLANTA', 'Planta'), ('CONTRATISTA', 'Contratista')],
        default='CONTRATISTA'
    )
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.profesion}"