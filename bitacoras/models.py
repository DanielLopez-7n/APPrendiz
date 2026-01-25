from django.db import models
# Importamos el modelo específico de Aprendiz
from aprendices.models import Aprendiz 
from empresas.models import Empresa

class Bitacora(models.Model):
    MODALIDADES = [
        ('CA', 'Contrato de Aprendizaje'),
        ('VL', 'Vínculo Laboral'),
        ('PP', 'Proyecto Productivo'),
        ('PA', 'Pasantía'),
        ('MO', 'Monitoría'),
    ]

    # CAMBIO: Ahora apunta a 'Aprendiz', no a cualquier usuario.
    # Esto evita que un Instructor tenga bitácoras por error.
    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE, related_name='bitacoras')
    
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name="Empresa")
    
    numero = models.PositiveIntegerField(verbose_name="Bitácora N°")
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha Fin")
    modalidad = models.CharField(max_length=2, choices=MODALIDADES, default='CA')
    
    # Estados
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    firmado_jefe = models.BooleanField(default=False, verbose_name="Aprobado por Empresa")
    evaluado_instructor = models.BooleanField(default=False, verbose_name="Evaluado por Instructor")
    observaciones_instructor = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-numero']
        # Evita que un aprendiz cree dos veces la bitácora #1
        unique_together = ['aprendiz', 'numero'] 

    def __str__(self):
        return f"Bitácora #{self.numero} - {self.aprendiz}"

class ActividadBitacora(models.Model):
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='actividades')
    descripcion = models.TextField(verbose_name="Descripción de la actividad")
    fecha_ejecucion = models.DateField(verbose_name="Fecha de ejecución")
    # Nota: Para usar FileField necesitamos configurar MEDIA_URL más adelante
    evidencia = models.FileField(upload_to='evidencias/', blank=True, null=True, verbose_name="Evidencia")
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Actividad: {self.descripcion[:30]}..."
    