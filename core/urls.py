from django.urls import path
from . import views 

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('panel_admin_base/', views.PanelAdmin_base, name='panel_admin_base'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search, name='search'),
    path('help/', views.help_page, name='help'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contactanos/', views.contactanos, name='contactanos'),


    ]