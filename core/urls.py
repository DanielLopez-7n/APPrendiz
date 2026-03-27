from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('panel_admin_base/', views.PanelAdmin_base, name='panel_admin_base'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search, name='search'),
    path('help/', views.help_page, name='help'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contactanos/', views.contactanos, name='contactanos'),
    path('busqueda/', views.busqueda_global, name='busqueda'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:index'), name='logout'),
    
    # --- Notificaciones ---
    path('notificaciones/marcar-leida/<int:pk>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('notificaciones/json/', views.obtener_notificaciones, name='obtener_notificaciones'),

    # --- Copias de Seguridad (Backups) ---
    path('backups/', views.listar_backups, name='listar_backups'),
    path('backups/crear/', views.crear_backup, name='crear_backup'),
    path('backups/restaurar/<str:nombre_archivo>/', views.restaurar_backup, name='restaurar_backup'),
    path('backups/descargar/<str:nombre_archivo>/', views.descargar_backup, name='descargar_backup'),
    path('backups/eliminar/<str:nombre_archivo>/', views.eliminar_backup, name='eliminar_backup'),
]
