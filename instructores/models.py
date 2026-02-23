from django.db import models
from django.contrib.auth.models import User

class Instructor(models.Model):
    # Relación 1 a 1 con el Usuario
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # --- 1. NUEVOS CAMPOS AÑADIDOS ---
    TIPO_DOC_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'), 
        ('CE', 'Cédula de Extranjería'), 
        ('PEP', 'PEP'), 
        ('PAS', 'Pasaporte')
    ]
    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOC_CHOICES, default='CC', verbose_name="Tipo de documento")
    correo_personal = models.EmailField(blank=True, null=True, verbose_name="Correo electrónico personal")
    direccion_residencia = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirección de residencia")
    
    # --- 2. TUS CAMPOS ORIGINALES (Intactos) ---
    # Nota: Le cambié el verbose_name a "Número de identificación" porque ahora puede ser un PEP o Pasaporte.
    cedula = models.CharField(max_length=20, verbose_name="Número de identificación")
    profesion = models.CharField(max_length=100, verbose_name="Profesión / Especialidad")
    
    # Respetamos tu longitud y el blank=True
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Celular")
    
    # Respetamos tus llaves en MAYÚSCULAS para no romper datos existentes
    tipo_contrato = models.CharField(
        max_length=50, 
        choices=[('PLANTA', 'Planta'), ('CONTRATISTA', 'Contratista')],
        default='CONTRATISTA'
    )
    
    def __str__(self):
        # Respetamos tu formato de visualización
        return f"{self.usuario.get_full_name()} - {self.profesion}"