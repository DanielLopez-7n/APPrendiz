from django.shortcuts import render
from .models import Programa # Importamos el modelo para mostrar los datos
from .forms import ProgramaForm # Importamos el formulario para crear nuevos programas
from django.shortcuts import render, redirect

def listar_programas(request):
    # Traemos todos los programas de la base de datos
    programas = Programa.objects.all()
    
    context = {
        'titulo': 'Programas de Formación',
        'programas': programas,
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