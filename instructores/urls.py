from django.urls import path
from . import views

app_name = 'instructores'

urlpatterns = [
    path('', views.listar_instructores, name='listar_instructores'),
]