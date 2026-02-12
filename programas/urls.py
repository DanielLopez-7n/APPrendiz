from django.urls import path
from . import views

app_name = 'programas'

urlpatterns = [
    path('', views.listar_programas, name='listar_programas'),
    path('crear/', views.crear_programa, name='crear_programa'),
]