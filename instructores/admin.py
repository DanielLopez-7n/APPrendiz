from django.contrib import admin
from .models import Instructor

# Esto habilita la tabla en el panel de control
@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'usuario', 'profesion', 'tipo_contrato')
    search_fields = ('cedula', 'usuario__first_name', 'usuario__last_name')