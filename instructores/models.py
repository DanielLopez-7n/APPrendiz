from django.db import models
from django.contrib.auth.models import User

class Instructor(models.Model):
    # Relación con el usuario (login)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Datos exclusivos del instructor
    profesion = models.CharField(max_length=100, verbose_name="Profesión / Especialidad")
    telefono = models.CharField(max_length=20, verbose_name="Celular")
    
    class Meta:
        verbose_name_plural = "Instructores" # Para que no diga "Instructors" en el admin

    def __str__(self):
        return f"Instructor: {self.usuario.first_name} {self.usuario.last_name}"