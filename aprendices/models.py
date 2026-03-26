from django.db import models
from django.contrib.auth.models import User

class Aprendiz(models.Model):
    # Relación principal
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 1. Identificación
    TIPO_DOC_CHOICES = [('CC', 'Cédula de Ciudadanía'), ('TI', 'Tarjeta de Identidad'), ('CE', 'Cédula de Extranjería'), ('PEP', 'PEP')]
    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOC_CHOICES, default='CC')
    documento = models.CharField(max_length=20, verbose_name="Número de identificación")
    
    # 2. Contacto y Residencia
    telefono = models.CharField(max_length=20, verbose_name="Contacto telefónico")
    correo_personal = models.EmailField(blank=True, null=True, verbose_name="Correo electrónico personal")
    direccion_residencia = models.CharField(max_length=200, blank=True, null=True)
    
    # 3. Información Académica SENA
    numero_ficha = models.ForeignKey('fichas.Ficha', on_delete=models.RESTRICT, verbose_name="Número de grupo")
    
    MODALIDAD_CHOICES = [('Presencial', 'Presencial'), ('Virtual', 'Virtual'), ('A distancia', 'A distancia')]
    modalidad_formacion = models.CharField(max_length=50, choices=MODALIDAD_CHOICES, default='Presencial')
    
    # 4. Etapa Productiva
    MODALIDAD_ETAPA_CHOICES = [('Presencial', 'Presencial'), ('Virtual', 'Virtual')]
    modalidad_etapa = models.CharField(max_length=50, choices=MODALIDAD_ETAPA_CHOICES, default='Presencial', verbose_name="Modalidad etapa productiva")
    etapa_exterior = models.BooleanField(default=False, verbose_name="¿Realiza etapa en el exterior?")
    pais_etapa = models.CharField(max_length=100, default='Colombia', verbose_name="País donde realiza la etapa")

    
    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - Ficha: {self.numero_ficha}"