from django.urls import path
from . import views

app_name = 'instructores'

urlpatterns = [
    path('', views.listar_instructores, name='listar_instructores'),
    path('nuevo/', views.crear_instructor, name='crear_instructor'),
    path('editar/<int:pk>/', views.editar_instructor, name='editar_instructor'),
    path('eliminar/<int:pk>/', views.eliminar_instructor, name='eliminar_instructor'),
    path('detalle/<int:pk>/', views.ver_detalle_instructor, name='ver_detalle_instructor'),
]