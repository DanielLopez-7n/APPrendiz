from django.db import models

class Empresa(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Razón Social")
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT")
    direccion = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    
    # Datos del Jefe Inmediato (Coformador)
    nombre_jefe = models.CharField(max_length=200, verbose_name="Nombre del Jefe Inmediato")
    cargo_jefe = models.CharField(max_length=100, verbose_name="Cargo")
    telefono_jefe = models.CharField(max_length=20, verbose_name="Teléfono de contacto")
    correo_jefe = models.EmailField(verbose_name="Correo electrónico")

    def __str__(self):
        return f"{self.nombre} - {self.nombre_jefe}"