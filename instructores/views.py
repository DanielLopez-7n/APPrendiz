from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Instructor
from .forms import InstructorForm

# Filtro de seguridad: Solo entra Staff o Superuser
def es_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(es_admin)
def listar_instructores(request):
    instructores = Instructor.objects.select_related('usuario').all()
    context = {'instructores': instructores}
    return render(request, 'instructores/listar_instructores.html', context)

@login_required
@user_passes_test(es_admin)
def crear_instructor(request):
    if request.method == 'POST':
        # Solo recibimos el formulario del instructor
        form = InstructorForm(request.POST)

        if form.is_valid():
            # 1. Guardamos el perfil del instructor
            instructor = form.save()
            
            # 2. ¡EL TOQUE MÁGICO! Le damos permisos de STAFF al usuario vinculado
            usuario = instructor.usuario
            usuario.is_staff = True
            usuario.save()

            messages.success(request, f'Perfil de instructor vinculado exitosamente. ¡Se le han otorgado permisos de Staff a {usuario.get_full_name()}!')
            return redirect('instructores:listar_instructores')
    else:
        form = InstructorForm()

    context = {
        'titulo': 'Vincular Perfil de Instructor',
        'form': form, # Cambiamos form_instructor a simplemente 'form'
        'editar': False
    }
    return render(request, 'instructores/crear_instructor.html', context)

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
