from django.urls import path
from . import views

app_name = 'bitacoras'

urlpatterns = [
    path('', views.listar_bitacoras, name='listar_bitacoras'),
    path('nueva/', views.crear_bitacora, name='crear_bitacora'),
    path('detalle/<int:pk>/', views.ver_bitacora, name='ver_bitacora'),
    # No se necesita editar y eliminar por ahora para simplificar, pero podrías agregarlos.
]