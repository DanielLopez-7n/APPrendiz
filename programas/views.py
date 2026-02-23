from django.shortcuts import render
from .models import Programa # Importamos el modelo para mostrar los datos
from .forms import ProgramaForm # Importamos el formulario para crear nuevos programas
from django.shortcuts import render, redirect
from django.db.models import Q


def listar_programas(request):
    programas = Programa.objects.all()
    query = request.GET.get('q', '')

    if query:
        programas = programas.filter(
            Q(nombre__icontains=query) 
        )

    context = {
        'programas': programas,
        'query': query
    }
    return render(request, 'programas/listar_programas.html', context)
def crear_programa(request):
    """Vista para registrar un nuevo programa de formación."""
    
    # Si el usuario envió el formulario (método POST)
    if request.method == 'POST':
        form = ProgramaForm(request.POST)
        if form.is_valid():
            # Guardamos el nuevo programa en la base de datos
            form.save()
            # Redirigimos a la lista de programas
            return redirect('programas:listar_programas')
    
    # Si el usuario solo está entrando a la página (método GET)
    else:
        form = ProgramaForm()

    context = {
        'titulo': 'Registrar Nuevo Programa',
        'form': form
    }
    # Renderizamos la plantilla que crearemos en el siguiente paso
    return render(request, 'programas/crear_programa.html', context)