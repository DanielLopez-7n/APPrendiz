from django.db import models
from django.conf import settings # Importante para vincular con tu app de usuarios

# 1. Modelo para guardar la información de la Empresa y el Jefe Inmediato
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

# 2. Modelo Principal: La Bitácora (Cabecera del Formato)
class Bitacora(models.Model):
    # Opciones de Modalidad (Las casillas de arriba del Excel)
    MODALIDADES = [
        ('CA', 'Contrato de Aprendizaje'),
        ('VL', 'Vínculo Laboral'),
        ('PP', 'Proyecto Productivo'),
        ('PA', 'Pasantía'),
        ('MO', 'Monitoría'),
    ]

    aprendiz = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bitacoras')
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, verbose_name="Empresa donde realiza prácticas")
    
    numero = models.PositiveIntegerField(verbose_name="Bitácora N°")
    fecha_inicio = models.DateField(verbose_name="Fecha Inicio del Período")
    fecha_fin = models.DateField(verbose_name="Fecha Fin del Período")
    modalidad = models.CharField(max_length=2, choices=MODALIDADES, default='CA')
    
    # Estados de Firma (Para el flujo de aprobación)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    firmado_jefe = models.BooleanField(default=False, verbose_name="Aprobado por Empresa")
    evaluado_instructor = models.BooleanField(default=False, verbose_name="Evaluado por Instructor")
    observaciones_instructor = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-numero'] # Ordenar de la más reciente a la más antigua
        unique_together = ['aprendiz', 'numero'] # Un aprendiz no puede tener dos bitácoras con el mismo número

    def __str__(self):
        return f"Bitácora #{self.numero} - {self.aprendiz}"

# 3. Modelo Detalle: Las Actividades 
class ActividadBitacora(models.Model):
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='actividades')
    descripcion = models.TextField(verbose_name="Descripción de la actividad")
    fecha_ejecucion = models.DateField(verbose_name="Fecha de ejecución") # O puedes usar inicio/fin si prefieres rango por actividad
    evidencia = models.FileField(upload_to='evidencias/', blank=True, null=True, verbose_name="Evidencia (Archivo/Foto)")
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Actividad: {self.descripcion[:30]}..."