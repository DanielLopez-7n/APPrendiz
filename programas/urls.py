from django.urls import path
from . import views

app_name = 'programas'

urlpatterns = [
    path('', views.listar_programas, name='listar_programas'),
    path('crear/', views.crear_programa, name='crear_programa'),
    path('editar/<int:pk>/', views.editar_programa, name='editar_programa'),
    path('eliminar/<int:pk>/', views.eliminar_programa, name='eliminar_programa'),
]