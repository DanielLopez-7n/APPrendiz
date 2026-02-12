from django.urls import path
from . import views

app_name = 'actividades'

urlpatterns = [
    path('', views.listar_actividades, name='listar_actividades'),
]