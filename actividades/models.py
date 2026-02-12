from django.db import models

class Actividad(models.Model):
    bitacora = models.ForeignKey('bitacoras.Bitacora', on_delete=models.CASCADE, related_name='detalles_actividades')
    descripcion = models.TextField(verbose_name="Descripción de la actividad")
    evidencia = models.CharField(max_length=255, verbose_name="Producto o Evidencia")

    def __str__(self):
        return f"Actividad de Bitácora {self.bitacora.numero_bitacora}"