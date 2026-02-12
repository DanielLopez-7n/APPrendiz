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
    


    ]