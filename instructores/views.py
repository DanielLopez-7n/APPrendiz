from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Instructor
from .forms import InstructorForm
from usuarios.forms import UsuarioForm

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
        form_usuario = UsuarioForm(request.POST)
        form_instructor = InstructorForm(request.POST)

        if form_usuario.is_valid() and form_instructor.is_valid():
            # 1. Preparar Usuario
            usuario = form_usuario.save(commit=False)
            documento = form_usuario.cleaned_data['username']
            
            # 2. Asignar contraseña automática y PERMISO STAFF
            usuario.set_password(documento)
            usuario.is_staff = True  # <--- ¡VITAL PARA INSTRUCTORES!
            usuario.save()
            
            # 3. Guardar Instructor
            instructor = form_instructor.save(commit=False)
            instructor.usuario = usuario
            instructor.save()

            messages.success(request, f'Instructor creado. Usuario y Clave: {documento}')
            return redirect('instructores:listar_instructores')
    else:
        form_usuario = UsuarioForm()
        form_instructor = InstructorForm()

    context = {
        'titulo': 'Registrar Instructor',
        'form_usuario': form_usuario,
        'form_instructor': form_instructor,
        'editar': False
    }
    return render(request, 'instructores/crear_instructor.html', context)

@login_required
@user_passes_test(es_admin)
def editar_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    usuario = instructor.usuario
    
    if request.method == 'POST':
        form_usuario = UsuarioForm(request.POST, instance=usuario)
        form_instructor = InstructorForm(request.POST, instance=instructor)
        
        if form_usuario.is_valid() and form_instructor.is_valid():
            form_usuario.save()
            form_instructor.save()
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('instructores:listar_instructores')
    else:
        form_usuario = UsuarioForm(instance=usuario)
        form_instructor = InstructorForm(instance=instructor)

    context = {
        'titulo': 'Editar Instructor',
        'form_usuario': form_usuario,
        'form_instructor': form_instructor,
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
    
    # --- AGREGAR ESTO AL FINAL DE instructores/views.py ---

@login_required
@user_passes_test(es_admin)
def ver_detalle_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    context = {
        'instructor': instructor,
        'titulo': f'Detalle del Instructor: {instructor.usuario.get_full_name()}'
    }
    return render(request, 'instructores/ver_detalle.html', context)
