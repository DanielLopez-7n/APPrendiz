
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Instructor
from .forms import InstructorForm
from django.db.models import Q


# Filtro de seguridad: Solo entra Staff o Superuser
def es_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(es_admin)
def listar_instructores(request):
    instructores = Instructor.objects.all()
    
    query = request.GET.get('q', '')
    tipo_contrato = request.GET.get('tipo_contrato', '')

    if query:
        instructores = instructores.filter(
            Q(cedula__icontains=query) |
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query) |
            Q(profesion__icontains=query)
        )
        
    if tipo_contrato:
        instructores = instructores.filter(tipo_contrato=tipo_contrato)

    context = {
        'instructores': instructores,
    }
    return render(request, 'instructores/listar_instructores.html', context)


@login_required
@user_passes_test(es_admin)
def editar_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    
    if request.method == 'POST':
        # Solo actualizamos los datos del perfil del instructor
        form = InstructorForm(request.POST, instance=instructor)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del instructor actualizados correctamente.')
            return redirect('instructores:listar_instructores')
    else:
        form = InstructorForm(instance=instructor)

    context = {
        'titulo': 'Editar Perfil de Instructor',
        'form': form,
        'editar': True
    }
    return render(request, 'instructores/crear_instructor.html', context)


@login_required
@user_passes_test(es_admin)
def eliminar_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    
    if instructor.usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('instructores:listar_instructores')

    if request.method == 'POST':
        instructor.usuario.delete()
        messages.success(request, 'Instructor eliminado.')
    
    return redirect('instructores:listar_instructores')
    
# Si es GET, mostramos la confirmación
@login_required
@user_passes_test(es_admin)
def ver_detalle_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    context = {
        'instructor': instructor,
        'titulo': f'Detalle del Instructor: {instructor.usuario.get_full_name()}'
    }
    return render(request, 'instructores/ver_detalle.html', context)
