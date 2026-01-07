from django.db import models
from django.conf import settings
# IMPORTANTE: Aquí importamos el modelo Empresa desde la otra app
from empresas.models import Empresa 

class Bitacora(models.Model):
    MODALIDADES = [
        ('CA', 'Contrato de Aprendizaje'),
        ('VL', 'Vínculo Laboral'),
        ('PP', 'Proyecto Productivo'),
        ('PA', 'Pasantía'),
        ('MO', 'Monitoría'),
    ]

    # NOTA: Por ahora lo dejamos vinculado al Usuario (settings.AUTH_USER_MODEL).
    # Más adelante, si quieres puntos extra, lo vincularemos al modelo 'Aprendiz'.
    aprendiz = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bitacoras')
    
    # Aquí usamos la Empresa que importamos arriba
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name="Empresa donde realiza prácticas")
    
    numero = models.PositiveIntegerField(verbose_name="Bitácora N°")
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio del Período")
    fecha_fin = models.DateField(verbose_name="Fecha Fin del Período")
    modalidad = models.CharField(max_length=2, choices=MODALIDADES, default='CA')
    
    # Estados de Firma
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    firmado_jefe = models.BooleanField(default=False, verbose_name="Aprobado por Empresa")
    evaluado_instructor = models.BooleanField(default=False, verbose_name="Evaluado por Instructor")
    observaciones_instructor = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-numero']
        unique_together = ['aprendiz', 'numero']

    def __str__(self):
        return f"Bitácora #{self.numero} - {self.aprendiz}"

class ActividadBitacora(models.Model):
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='actividades')
    descripcion = models.TextField(verbose_name="Descripción de la actividad")
    fecha_ejecucion = models.DateField(verbose_name="Fecha de ejecución")
    evidencia = models.FileField(upload_to='evidencias/', blank=True, null=True, verbose_name="Evidencia (Archivo/Foto)")
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Actividad: {self.descripcion[:30]}..."