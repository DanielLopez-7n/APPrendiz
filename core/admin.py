from django.contrib import admin
from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'usuario_destino', 'leida', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario_destino__username')
    list_editable = ('leida',)
    ordering = ('-fecha_creacion',)
