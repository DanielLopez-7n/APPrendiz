from django.db import models
from django.db.models import Max
# Importamos los modelos de tus otras apps
from aprendices.models import Aprendiz
from instructores.models import Instructor
from fichas.models import Ficha 

class Bitacora(models.Model):
    # --- LISTAS DESPLEGABLES (CHOICES) DEL FORMATO V5 ---
    MODALIDAD_CHOICES = [
        ('Presencial', 'Presencial'),
        ('Virtual', 'Virtual'),
        ('Mixta', 'Mixta'),
    ]
    
    TIPO_DOC_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
    ]

    RIESGO_ARL_CHOICES = [
        ('I', 'I - Riesgo Mínimo'),
        ('II', 'II - Riesgo Bajo'),
        ('III', 'III - Riesgo Medio'),
        ('IV', 'IV - Riesgo Alto'),
        ('V', 'V - Riesgo Máximo'),
    ]

    SI_NO_NA_CHOICES = [
        ('SI', 'Sí'),
        ('NO', 'No'),
        ('NA', 'No Aplica'),
    ]

    # --- RELACIONES PRINCIPALES ---
    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE)
    
    # Aquí conectamos con tu nueva App de Fichas
    ficha = models.ForeignKey(
        Ficha, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Ficha de Caracterización"
    )
    
    instructor_seguimiento = models.ForeignKey(
        Instructor, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='bitacoras_seguimiento', 
        verbose_name="Instructor de Seguimiento"
    )

    # --- MÓDULO 1: GENERALIDADES ---
    # blank=True y null=True para evitar el error de "non-editable" al migrar
    numero_bitacora = models.PositiveIntegerField(verbose_name="Número de Bitácora", blank=True, null=True)
    fecha_inicio = models.DateField(verbose_name="Período: Desde")
    fecha_fin = models.DateField(verbose_name="Período: Hasta")
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOC_CHOICES, default='CC')

    # --- MÓDULO 2: DATOS DEL ENTE CO-FORMADOR (EMPRESA) ---
    razon_social_empresa = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    nit_empresa = models.CharField(max_length=20, verbose_name="NIT")
    direccion_empresa = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirección")
    
    nombre_jefe = models.CharField(max_length=150, verbose_name="Nombre Jefe Inmediato")
    cargo_jefe = models.CharField(max_length=100, verbose_name="Cargo")
    telefono_jefe = models.CharField(max_length=20, verbose_name="Teléfono")
    email_jefe = models.EmailField(verbose_name="Email")

    # --- MÓDULO 3: MODALIDAD Y SEGURIDAD (SST) ---
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='Presencial')
    pais_etapa = models.CharField(max_length=50, default='Colombia')
    
    afiliado_arl = models.CharField(max_length=2, choices=SI_NO_NA_CHOICES, verbose_name="¿Afiliado a ARL?")
    nivel_riesgo = models.CharField(max_length=3, choices=RIESGO_ARL_CHOICES, verbose_name="Nivel de Riesgo")
    uso_epp = models.CharField(max_length=3, choices=SI_NO_NA_CHOICES, verbose_name="¿Cuenta con EPP?")

    # --- ESTADOS Y CONTROL ---
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Evaluada', 'Evaluada'), 
        ('Rechazada', 'Rechazada'), 
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    observaciones_instructor = models.TextField(blank=True, null=True)

    # LÓGICA DE NUMERACIÓN AUTOMÁTICA (1, 2, 3...)
    def save(self, *args, **kwargs):
        if not self.pk: # Solo si es nueva
            ultimo_numero = Bitacora.objects.filter(aprendiz=self.aprendiz).aggregate(Max('numero_bitacora'))['numero_bitacora__max']
            self.numero_bitacora = (ultimo_numero or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bitácora {self.numero_bitacora} - {self.aprendiz}"


# --- EL MODELO HIJO (LAS FILAS DEL EXCEL) ---
class ActividadBitacora(models.Model):
    # Relación: Una bitácora tiene muchas actividades
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='actividades')
    
    descripcion = models.TextField(verbose_name="Descripción de la actividad")
    fecha_ejecucion = models.DateField(verbose_name="Fecha de Ejecución")
    evidencia = models.CharField(max_length=255, verbose_name="Evidencia / Producto", blank=True, null=True)

    def __str__(self):
        return f"Actividad {self.id} de Bitácora {self.bitacora.numero_bitacora}"
    
    