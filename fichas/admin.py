from django.contrib import admin
from .models import Ficha

@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'programa', 'fecha_fin')
    search_fields = ('numero', 'programa__nombre')