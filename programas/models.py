from django.db import models

class Programa(models.Model):
    NIVEL_CHOICES = [
        ('Tecnico', 'Técnico'),
        ('Tecnologo', 'Tecnólogo'),
        ('Especializacion', 'Especialización'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Programa")
    codigo = models.CharField(max_length=50, verbose_name="Código del Programa")
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='Tecnologo')
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
    
    