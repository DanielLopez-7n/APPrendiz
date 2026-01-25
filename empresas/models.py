from django.db import models

class Empresa(models.Model):
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT")
    nombre = models.CharField(max_length=150, verbose_name="Razón Social")
    direccion = models.CharField(max_length=200, verbose_name="Dirección", blank=True, null=True)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    
    # Datos del contacto en la empresa (Jefe Inmediato)
    encargado = models.CharField(max_length=100, verbose_name="Jefe Inmediato / Contacto")
    email_encargado = models.EmailField(verbose_name="Correo del Encargado", blank=True, null=True)
    
    # Auditoría (opcional pero recomendada: cuándo se creó)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.nit})"
    