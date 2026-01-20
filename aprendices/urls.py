from django.urls import path
from . import views

app_name = 'aprendices'

urlpatterns = [
    path('', views.listar_aprendices, name='listar_aprendices'),
    path('registrar/', views.crear_aprendiz, name='crear_aprendiz'),
    path('editar/<int:pk>/', views.editar_aprendiz, name='editar_aprendiz'),
    path('eliminar/<int:pk>/', views.eliminar_aprendiz, name='eliminar_aprendiz'),
    path('detalle/<int:pk>/', views.ver_detalle_aprendiz, name='ver_detalle_aprendiz'),
    path('mi-perfil/', views.perfil_aprendiz, name='perfil_aprendiz'),
]
