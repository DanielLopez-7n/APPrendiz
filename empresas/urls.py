from django.urls import path
from . import views

app_name = 'empresas' 

urlpatterns = [
    path('', views.listar_empresas, name='listar_empresas'),    
    path('nueva/', views.crear_empresa, name='crear_empresa'),    
    path('editar/<int:pk>/', views.editar_empresa, name='editar_empresa'),    
    path('eliminar/<int:pk>/', views.eliminar_empresa, name='eliminar_empresa'),
]