from django.shortcuts import render, redirect
from django.contrib import messages # Para mandar mensajes de "Guardado con éxito"
from .forms import UsuarioForm, AprendizForm
from django.contrib.auth.decorators import login_required # <--- 1. Importar login requiered

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
