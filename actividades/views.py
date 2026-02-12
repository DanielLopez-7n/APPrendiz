from django.shortcuts import render

def listar_actividades(request):
    return render(request, 'actividades/listar_actividades.html')