from django.db import models
from django.contrib.auth.models import User

class Aprendiz(models.Model):
    # Relación 1 a 1: Un usuario del sistema es UN aprendiz
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Datos exclusivos del SENA
    numero_ficha = models.CharField(max_length=20, verbose_name="Número de Ficha")
    programa_formacion = models.CharField(max_length=150, verbose_name="Programa de Formación")
    telefono = models.CharField(max_length=20, verbose_name="Celular")
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - Ficha: {self.numero_ficha}"