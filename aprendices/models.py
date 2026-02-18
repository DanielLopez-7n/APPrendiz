from django.db import models
from django.contrib.auth.models import User

class Aprendiz(models.Model):
    # Relación 1 a 1: Un usuario del sistema es UN aprendiz
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # --- AQUÍ ESTÁ LA MAGIA DE LAS LLAVES FORÁNEAS ---
    # En lugar de CharField, usamos ForeignKey apuntando a las otras apps
    numero_ficha = models.ForeignKey('fichas.Ficha', on_delete=models.RESTRICT, verbose_name="Número de Ficha")
    programa_formacion = models.ForeignKey('programas.Programa', on_delete=models.RESTRICT, verbose_name="Programa de Formación")
    
    # Datos exclusivos del SENA
    telefono = models.CharField(max_length=20, verbose_name="Celular")
    documento = models.CharField(max_length=20, null=True, blank=True, verbose_name="Documento de Identidad")
    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - Ficha: {self.numero_ficha}"