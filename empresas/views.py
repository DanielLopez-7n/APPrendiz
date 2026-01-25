from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Empresa
from .forms import EmpresaForm

# Función de seguridad: Solo permite entrar a Staff (Instructores y Admins)
def es_staff(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(es_staff)
def listar_empresas(request):
    # Traemos todas las empresas para mostrarlas en la tabla
    empresas = Empresa.objects.all()
    context = {
        'empresas': empresas,
        'titulo': 'Gestión de Empresas'
    }
    return render(request, 'empresas/listar_empresas.html', context)

@login_required
@user_passes_test(es_staff)
def crear_empresa(request):
    if request.method == 'POST':
        # Si enviaron datos, intentamos guardar
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa registrada exitosamente.')
            return redirect('empresas:listar_empresas')
    else:
        # Si apenas entran, mostramos el formulario vacío
        form = EmpresaForm()

    context = {
        'form': form,
        'titulo': 'Registrar Empresa',
        'editar': False
    }
    return render(request, 'empresas/crear_empresa.html', context)

@login_required
@user_passes_test(es_staff)
def editar_empresa(request, pk):
    # Buscamos la empresa por su ID (pk)
    empresa = get_object_or_404(Empresa, pk=pk)
    
    if request.method == 'POST':
        # Actualizamos los datos existentes
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos de la empresa actualizados.')
            return redirect('empresas:listar_empresas')
    else:
        # Mostramos el formulario con los datos cargados
        form = EmpresaForm(instance=empresa)

    context = {
        'form': form,
        'titulo': 'Editar Empresa',
        'editar': True
    }
    return render(request, 'empresas/crear_empresa.html', context)

@login_required
@user_passes_test(es_staff)
def eliminar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    
    if request.method == 'POST':
        empresa.delete()
        messages.success(request, 'Empresa eliminada del sistema.')
        return redirect('empresas:listar_empresas')
    