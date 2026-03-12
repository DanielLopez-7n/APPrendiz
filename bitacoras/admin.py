from django.contrib import admin
from .models import Bitacora, ActividadBitacora

class ActividadBitacoraInline(admin.TabularInline):
    model = ActividadBitacora
    extra = 1

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    # Mostramos los campos principales del V5
    list_display = ('numero_bitacora', 'nombre_completo_aprendiz', 'nombre_empresa', 'estado')
    list_filter = ('estado', 'modalidad_ejecucion', 'arl_afiliado', 'alternativa_etapa')
    search_fields = ('nombre_completo_aprendiz', 'numero_identificacion_aprendiz', 'nombre_empresa')
    inlines = [ActividadBitacoraInline]

@admin.register(ActividadBitacora)
class ActividadBitacoraAdmin(admin.ModelAdmin):
    # AQUÍ ESTABA EL ERROR: Cambiamos 'evidencia' por 'evidencia_cumplimiento'
    list_display = ('bitacora', 'periodo_mes', 'evidencia_cumplimiento')
    search_fields = ('descripcion_actividad', 'periodo_mes')