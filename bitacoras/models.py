from django.db import models
from django.db.models import Max
from aprendices.models import Aprendiz
from instructores.models import Instructor
from fichas.models import Ficha
from empresas.models import Empresa

class Bitacora(models.Model):
    # --- OPCIONES DEL FORMATO ---
    CLASIFICACION_CHOICES = [('Pública', 'Pública'), ('Pública Clasificada', 'Pública Clasificada'), ('Pública Reservada', 'Pública Reservada')]
    TIPO_DOC_CHOICES = [('CC', 'Cédula de Ciudadanía'), ('TI', 'Tarjeta de Identidad'), ('CE', 'Cédula de Extranjería')]
    MODALIDAD_FORMACION_CHOICES = [('Presencial', 'Presencial'), ('Virtual', 'Virtual'), ('A distancia', 'A distancia')]
    MODALIDAD_EJECUCION_CHOICES = [('Presencial', 'Presencial'), ('Virtual', 'Virtual'), ('Mixta', 'Mixta')]
    ALTERNATIVA_CHOICES = [
        ('Contrato de aprendizaje', 'Contrato de aprendizaje'), ('Vínculo laboral', 'Vínculo laboral'),
        ('Proyecto productivo', 'Proyecto productivo'), ('Monitoria', 'Monitoria'),
        ('Apoyo a entidad estatal/ONG', 'Apoyo a entidad estatal/ONG'), ('Asesoría a PYMES', 'Asesoría a PYMES'), ('Pasantía', 'Pasantía')
    ]
    RIESGO_ARL_CHOICES = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    SI_NO_CHOICES = [('SI', 'Sí'), ('NO', 'No')]
    SI_NO_NA_CHOICES = [('SI', 'Sí'), ('NO', 'No'), ('NA', 'No Aplica')]

    # --- RELACIONES INTERNAS ---
    aprendiz_rel = models.ForeignKey(Aprendiz, on_delete=models.CASCADE)
    
    # --- ENCABEZADO Y CLASIFICACIÓN ---
    clasificacion_informacion = models.CharField(max_length=50, choices=CLASIFICACION_CHOICES, default='Pública')
    numero_bitacora = models.PositiveIntegerField(verbose_name="Bitácora N°")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    # --- DATOS DEL APRENDIZ (TAL CUAL EL EXCEL) ---
    nombre_completo_aprendiz = models.CharField(max_length=150)
    tipo_documento_aprendiz = models.CharField(max_length=5, choices=TIPO_DOC_CHOICES)
    numero_identificacion_aprendiz = models.CharField(max_length=20)
    contacto_telefonico_aprendiz = models.CharField(max_length=20)
    correo_institucional_aprendiz = models.EmailField()
    correo_personal_aprendiz = models.EmailField()
    direccion_residencia_aprendiz = models.CharField(max_length=200)
    numero_grupo_ficha = models.CharField(max_length=50)
    modalidad_formacion = models.CharField(max_length=50, choices=MODALIDAD_FORMACION_CHOICES)
    programa_formacion = models.CharField(max_length=150)
    modalidad_ejecucion = models.CharField(max_length=20, choices=MODALIDAD_EJECUCION_CHOICES)
    exterior = models.CharField(max_length=2, choices=SI_NO_CHOICES)
    pais_etapa = models.CharField(max_length=100)
    alternativa_etapa = models.CharField(max_length=100, choices=ALTERNATIVA_CHOICES)

    # --- DATOS DEL ENTE CO-FORMADOR ---
    nombre_empresa = models.CharField(max_length=150)
    nit_empresa = models.CharField(max_length=50)
    direccion_empresa = models.CharField(max_length=200)

    # --- DATOS DEL JEFE INMEDIATO / SUPERVISOR ---
    nombre_jefe = models.CharField(max_length=150)
    cargo_jefe = models.CharField(max_length=100)
    telefono_jefe = models.CharField(max_length=20)
    email_jefe = models.EmailField()

    # --- DATOS DEL INSTRUCTOR DE SEGUIMIENTO (LO QUE FALTABA) ---
    nombre_instructor_seguimiento = models.CharField(max_length=150)
    email_instructor_seguimiento = models.EmailField()
    telefono_instructor_seguimiento = models.CharField(max_length=20, blank=True, null=True)

    # --- SEGURIDAD Y SALUD EN EL TRABAJO ---
    arl_afiliado = models.CharField(max_length=2, choices=SI_NO_CHOICES)
    nivel_riesgo = models.CharField(max_length=2, choices=RIESGO_ARL_CHOICES)
    riesgo_corresponde = models.CharField(max_length=2, choices=SI_NO_CHOICES)
    cuenta_epp = models.CharField(max_length=3, choices=SI_NO_NA_CHOICES)
    
    # --- ANEXOS Y FIRMAS ---
    anexo_fotografico = models.ImageField(upload_to='anexos_bitacoras/', blank=True, null=True)
    firma_aprendiz = models.ImageField(upload_to='firmas/', blank=True, null=True)
    firma_jefe = models.ImageField(upload_to='firmas/', blank=True, null=True)
    firma_instructor = models.ImageField(upload_to='firmas/', blank=True, null=True)

    # --- CONTROL ---
    ESTADOS = [('Pendiente', 'Pendiente'), ('Evaluada', 'Evaluada'), ('Rechazada', 'Rechazada')]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha_entrega_bitacora = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            ultimo = Bitacora.objects.filter(aprendiz_rel=self.aprendiz_rel).aggregate(Max('numero_bitacora'))['numero_bitacora__max']
            self.numero_bitacora = (ultimo or 0) + 1
        super().save(*args, **kwargs)

class ActividadBitacora(models.Model):
    bitacora = models.ForeignKey(Bitacora, on_delete=models.CASCADE, related_name='actividades')
    # Columnas exactas de la tabla del Excel
    descripcion_actividad = models.TextField()
    competencias_asociadas = models.TextField()
    periodo_mes = models.CharField(max_length=50)
    evidencia_cumplimiento = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True, null=True)