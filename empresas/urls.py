from django.urls import path
from . import views

# Esto define el "apellido" de las rutas (namespace)
# Sin esto, el error "empresas is not a registered namespace" seguirá saliendo.
app_name = 'empresas' 

urlpatterns = [
    # Ruta para listar: www.tusitio.com/empresas/
    path('', views.listar_empresas, name='listar_empresas'),
    
    # Ruta para crear: www.tusitio.com/empresas/nueva/
    path('nueva/', views.crear_empresa, name='crear_empresa'),
    
    # Ruta para editar: www.tusitio.com/empresas/editar/1/
    path('editar/<int:pk>/', views.editar_empresa, name='editar_empresa'),
    
    # Ruta para eliminar: www.tusitio.com/empresas/eliminar/1/
    path('eliminar/<int:pk>/', views.eliminar_empresa, name='eliminar_empresa'),
]