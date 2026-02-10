
from django.contrib import admin
from .models import Bitacora 

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    # Mostramos las columnas más importantes en la lista
    list_display = ('numero_bitacora', 'aprendiz', 'fecha_inicio', 'fecha_fin', 'estado')
    
    # Filtros laterales útiles
    list_filter = ('estado', 'modalidad', 'afiliado_arl')
    
    # Barra de búsqueda (busca por nombre del aprendiz o número)
    search_fields = ('aprendiz__usuario__first_name', 'aprendiz__usuario__last_name', 'numero_bitacora')