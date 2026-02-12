from django.db import models
from programas.models import Programa

class Ficha(models.Model):
    numero = models.CharField(max_length=20, primary_key=True, verbose_name="Número de Ficha")
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='fichas')

    def __str__(self):
        return f"{self.numero} - {self.programa.nombre}"