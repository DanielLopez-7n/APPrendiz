from django.db import models

class Programa(models.Model):
    codigo = models.CharField(max_length=20, primary_key=True, verbose_name="Código del Programa")
    nombre = models.CharField(max_length=255, verbose_name="Nombre del Programa")

    def __str__(self):
        return self.nombre