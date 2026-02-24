from django.urls import path
from . import views

app_name = 'fichas'

urlpatterns = [
    path('', views.listar_fichas, name='listar_fichas'),
    path('crear/', views.crear_ficha, name='crear_ficha'),
    path('editar/<int:pk>/', views.editar_ficha, name='editar_ficha'),
    path('eliminar/<int:pk>/', views.eliminar_ficha, name='eliminar_ficha'),
]