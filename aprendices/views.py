from django.shortcuts import render, redirect, get_object_or_404 # <--- AQUÍ ESTÁ EL ARREGLO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Aprendiz 
from .forms import UsuarioForm, AprendizForm
from usuarios.forms import UsuarioForm

# Vista para Listar todos los Aprendices
@login_required
def listar_aprendices(request):
    # 1. Consultamos todos los aprendices en la base de datos
    aprendices = Aprendiz.objects.all()
    
    context = {
        'aprendices': aprendices
    }
    return render(request, 'aprendices/listar_aprendices.html', context)

# Vista para Registrar un nuevo Aprendiz
@login_required
def crear_aprendiz(request):
    if request.method == 'POST':
        # Si el usuario llenó el formulario y le dio "Guardar"
        form_usuario = UsuarioForm(request.POST)
        form_aprendiz = AprendizForm(request.POST)

        # Validamos que los dos formularios estén bien
        if form_usuario.is_valid() and form_aprendiz.is_valid():
            # 1. Guardamos el Usuario primero (pero aún no el aprendiz)
            usuario = form_usuario.save()
            
            # 2. Preparamos el Aprendiz, pero no lo guardamos en bd todavía (commit=False)
            aprendiz = form_aprendiz.save(commit=False)
            
            # 3. Hacemos la conexión manual. Asignamos el usuario recién creado al aprendiz
            aprendiz.usuario = usuario
            
            # 4. Ahora sí guardamos el Aprendiz definitivamente
            aprendiz.save()

            messages.success(request, 'El aprendiz se ha registrado correctamente.')
            return redirect('aprendices:crear_aprendiz')
    else:
        # Si entramos a la página por primera vez mostramos los formularios vacíos
        form_usuario = UsuarioForm()
        form_aprendiz = AprendizForm()

    context = {
        'form_usuario': form_usuario,
        'form_aprendiz': form_aprendiz
    }
    
    return render(request, 'aprendices/crear_aprendiz.html', context)

# --- VISTA PARA EDITAR (UPDATE) ---
@login_required
def editar_aprendiz(request, pk):
    # 1. Buscamos el aprendiz por su id, si no existe sale error 404.
    aprendiz = get_object_or_404(Aprendiz, pk=pk)
    usuario = aprendiz.usuario # Obtenemos el usuario relacionado
    
    if request.method == 'POST':
        # Cargamos los formularios con los datos que vienen del navegador (POST)
        # Y le decimos qué "instance" (objeto) van a modificar
        form_usuario = UsuarioForm(request.POST, instance=usuario)
        form_aprendiz = AprendizForm(request.POST, instance=aprendiz)
        
        if form_usuario.is_valid() and form_aprendiz.is_valid():
            form_usuario.save()
            form_aprendiz.save()
            messages.success(request, f'Aprendiz {usuario.first_name} actualizado correctamente.')
            return redirect('aprendices:listar_aprendices')
            
    else:
        # Si es GET (apenas entramos a la página) cargamos los formularios llenos con los datos actuales
        form_usuario = UsuarioForm(instance=usuario)
        form_aprendiz = AprendizForm(instance=aprendiz)
    
    context = {
        'form_usuario': form_usuario,
        'form_aprendiz': form_aprendiz,
        'aprendiz': aprendiz, # Pasamos el objeto para usarlo en el título
        'editar': True # Una banderita para cambiar el texto del botón en el HTML
    }
    # Reutilizamos la misma plantilla de crear aprendiz
    return render(request, 'aprendices/crear_aprendiz.html', context)

# --- VISTA PARA ELIMINAR (DELETE) ---
@login_required
def eliminar_aprendiz(request, pk):
    aprendiz = get_object_or_404(Aprendiz, pk=pk)
    
    # Borramos al usuario (y por cascada se borra el aprendiz)
    aprendiz.usuario.delete()
    
    messages.success(request, 'Aprendiz eliminado correctamente.')
    return redirect('aprendices:listar_aprendices')


# ---  VISTA PARA VER DETALLES DE UN APRENDIZ ---
@login_required
def ver_detalle_aprendiz(request, pk):
    aprendiz = get_object_or_404(Aprendiz, pk=pk)
    context = {
        'aprendiz': aprendiz
    }
    return render(request, 'aprendices/ver_detalle.html', context)