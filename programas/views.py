from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Programa
from .forms import ProgramaForm

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
    # CORRECCIÓN: Apuntamos a la lista, NO al formulario
    return render(request, 'programas/listar_programas.html', context)

def crear_programa(request):
    """Vista para registrar un nuevo programa de formación."""
    if request.method == 'POST':
        form = ProgramaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programa de formación creado exitosamente.')
            return redirect('programas:listar_programas')
    else:
        form = ProgramaForm()

    context = {
        'accion': 'Crear',  # CORRECCIÓN: Cambiamos 'titulo' por 'accion' para el HTML dinámico
        'form': form
    }
    return render(request, 'programas/form_programa.html', context)

def editar_programa(request, pk):
    programa = get_object_or_404(Programa, pk=pk)
    
    if request.method == 'POST':
        form = ProgramaForm(request.POST, instance=programa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Programa "{programa.nombre}" actualizado correctamente.')
            return redirect('programas:listar_programas')
    else:
        form = ProgramaForm(instance=programa)

    return render(request, 'programas/form_programa.html', {'form': form, 'accion': 'Editar'})

def eliminar_programa(request, pk):
    programa = get_object_or_404(Programa, pk=pk)
    nombre = programa.nombre
    programa.delete()
    messages.success(request, f'El programa "{nombre}" ha sido eliminado correctamente.')
    return redirect('programas:listar_programas')