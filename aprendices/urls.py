from django.urls import path
from . import views

app_name = 'aprendices'

urlpatterns = [
    path('registrar/', views.crear_aprendiz, name='crear_aprendiz'),
    # Ruta para VER la lista (la dejamos vacía '' para que sea la principal de aprendices)
    path('', views.listar_aprendices, name='listar_aprendices'),
]