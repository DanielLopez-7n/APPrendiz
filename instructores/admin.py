from django.contrib import admin
from .models import Instructor

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    # Aquí cambiamos 'cedula' por 'usuario' y agregamos 'telefono'
    list_display = ('id', 'usuario', 'profesion', 'telefono', 'tipo_contrato')
    
    # Para buscar por nombre de usuario o profesión
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'profesion')
    
    # Filtros laterales
    list_filter = ('tipo_contrato',)