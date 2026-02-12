from django.db import models
from programas.models import Programa # Importamos la relación

class Ficha(models.Model):
    numero = models.CharField(max_length=50, unique=True, verbose_name="Número de Ficha")
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, verbose_name="Programa de Formación")
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio Lectiva")
    fecha_fin = models.DateField(verbose_name="Fecha Fin Lectiva")
    
    def __str__(self):
        return f"{self.numero} - {self.programa.nombre}"