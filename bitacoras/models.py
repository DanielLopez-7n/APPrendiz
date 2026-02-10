# bitacoras/models.py

from django.db import models
from aprendices.models import Aprendiz
from instructores.models import Instructor

class Bitacora(models.Model):
    # --- OPCIONES DE SELECCIÓN (DROPDOWNS) ---
    MODALIDAD_CHOICES = [
        ('Presencial', 'Presencial'),
        ('Virtual', 'Virtual'),
        ('Mixta', 'Mixta'),
    ]
    
    RIESGO_ARL_CHOICES = [
        ('1', 'I - Riesgo Mínimo'),
        ('2', 'II - Riesgo Bajo'),
        ('3', 'III - Riesgo Medio'),
        ('4', 'IV - Riesgo Alto'),
        ('5', 'V - Riesgo Máximo'),
    ]

    SI_NO_NA_CHOICES = [
        ('SI', 'Sí'),
        ('NO', 'No'),
        ('NA', 'No Aplica'),
    ]

    # --- RELACIONES ---
    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE)
    # Lista desplegable de instructores (clave para tu requerimiento)
    instructor_seguimiento = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='bitacoras_seguimiento', verbose_name="Instructor de Seguimiento")
    
    # --- 1. GENERALIDADES ---
    numero_bitacora = models.PositiveIntegerField(verbose_name="Número de Bitácora", default=1)
    fecha_inicio = models.DateField(verbose_name="Período: Desde")
    fecha_fin = models.DateField(verbose_name="Período: Hasta")
    
    # --- 2. DATOS DEL ENTE CO-FORMADOR (EMPRESA) ---
    razon_social_empresa = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    nit_empresa = models.CharField(max_length=20, verbose_name="NIT")
    direccion_empresa = models.CharField(max_length=200, verbose_name="Dirección de la Empresa", null=True, blank=True)
    
    nombre_jefe_inmediato = models.CharField(max_length=150, verbose_name="Nombre Jefe Inmediato")
    cargo_jefe = models.CharField(max_length=100, verbose_name="Cargo")
    telefono_jefe = models.CharField(max_length=20, verbose_name="Teléfono Jefe")
    email_jefe = models.EmailField(verbose_name="Email Jefe")

    # --- 3. MODALIDAD Y SEGURIDAD (ARL - Clave en V5) ---
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='Presencial', verbose_name="Modalidad Etapa Productiva")
    pais_etapa = models.CharField(max_length=50, default='Colombia', verbose_name="País") 
    
    afiliado_arl = models.CharField(max_length=2, choices=[('SI', 'Sí'), ('NO', 'No')], default='SI', verbose_name="¿Afiliado a ARL?")
    nivel_riesgo = models.CharField(max_length=1, choices=RIESGO_ARL_CHOICES, verbose_name="Nivel de Riesgo")
    riesgo_corresponde = models.CharField(max_length=2, choices=[('SI', 'Sí'), ('NO', 'No')], verbose_name="¿Riesgo corresponde a actividades?", default='SI')
    uso_epp = models.CharField(max_length=3, choices=SI_NO_NA_CHOICES, verbose_name="¿Cuenta con EPP?", default='SI')

    # --- 4. ACTIVIDADES ---
    descripcion_actividades = models.TextField(verbose_name="Descripción de actividades realizadas")
    
    # Archivos y Estados
    archivo_evidencia = models.FileField(upload_to='bitacoras/', null=True, blank=True, verbose_name="Evidencia (PDF/Foto)")
    
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Evaluada', 'Evaluada'), 
        ('Rechazada', 'Rechazada'), 
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    observaciones_instructor = models.TextField(blank=True, null=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bitácora {self.numero_bitacora} - {self.aprendiz.usuario.get_full_name()}"