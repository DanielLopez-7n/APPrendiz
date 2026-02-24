from django.shortcuts import render
from .models import Ficha
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import FichaForm

def listar_fichas(request):
    fichas = Ficha.objects.all()
    query = request.GET.get('q', '')

    if query:
        fichas = fichas.filter(
            Q(numero__icontains=query) |
            Q(programa__nombre__icontains=query)
        )

    context = {
        'fichas': fichas,
    }
    return render(request, 'fichas/listar_fichas.html', context)

def crear_ficha(request):
    if request.method == 'POST':
        form = FichaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ficha creada exitosamente.')
            return redirect('fichas:listar_fichas')
    else:
        form = FichaForm()

    context = {'accion': 'Crear', 'form': form}
    return render(request, 'fichas/form_ficha.html', context)

def editar_ficha(request, pk):
    ficha = get_object_or_404(Ficha, pk=pk)
    
    if request.method == 'POST':
        form = FichaForm(request.POST, instance=ficha)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ficha {ficha.numero} actualizada correctamente.')
            return redirect('fichas:listar_fichas')
    else:
        form = FichaForm(instance=ficha)

    context = {'accion': 'Editar', 'form': form}
    return render(request, 'fichas/form_ficha.html', context)

def eliminar_ficha(request, pk):
    ficha = get_object_or_404(Ficha, pk=pk)
    numero = ficha.numero
    ficha.delete()
    messages.success(request, f'La ficha {numero} ha sido eliminada.')
    return redirect('fichas:listar_fichas')