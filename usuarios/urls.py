# usuarios/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from core.views import CustomLoginView
from . import views
app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:index'), name='logout'),
    
    # Perfil de usuario
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Panel de administración
    path('usuarios/', views.lista_usuarios_view, name='lista_usuarios'),
    path('crear/', views.crear_usuario_con_perfil, name='crear_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario_view, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario_view, name='eliminar_usuario'),
    path('detalle/<int:user_id>/', views.ver_detalle_usuario, name='ver_detalle_usuario'),
    path('perfil/', views.perfil_view, name='ver_perfil'),
    path('perfil/editar/', views.editar_mi_perfil, name='editar_mi_perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]