from django.db import models
from django.contrib.auth.models import User

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('bitacora_nueva', 'Nueva Bitácora'),
        ('bitacora_evaluada', 'Bitácora Evaluada'),
        ('alerta_sistema', 'Alerta del Sistema'),
    ]

    usuario_destino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='alerta_sistema')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    enlace = models.CharField(max_length=255, blank=True, null=True, help_text="URL a la que llevará al hacer clic")
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} - {self.usuario_destino.username}"