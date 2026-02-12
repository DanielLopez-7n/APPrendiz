from django.urls import path
from . import views

app_name = 'fichas'

urlpatterns = [
    path('', views.listar_fichas, name='listar_fichas'),
]