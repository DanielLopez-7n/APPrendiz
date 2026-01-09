from django.urls import path
from . import views

app_name = 'aprendices'

urlpatterns = [
    path('registrar/', views.crear_aprendiz, name='crear_aprendiz'),
]