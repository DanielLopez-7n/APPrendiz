from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AprendizForm
from .models import Aprendiz
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from bitacoras.models import Bitacora
from django.db.models import Q

# Vista para Listar todos los Aprendices
@login_required
def listar_aprendices(request):
    aprendices = Aprendiz.objects.all()
    
    # 1. Capturamos lo que el usuario escribió en la barra
    query = request.GET.get('q', '')
    modalidad = request.GET.get('modalidad', '')

    # 2. Si escribió algo, filtramos por nombre, apellido, documento o ficha
    if query:
        aprendices = aprendices.filter(
            Q(documento__icontains=query) |
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query) |
            Q(numero_ficha__numero__icontains=query)
        )
    
    # 3. Si seleccionó un filtro del desplegable
    if modalidad:
        aprendices = aprendices.filter(modalidad_formacion=modalidad)

    context = {
        'aprendices': aprendices,
        # Opcional: mandamos la query de vuelta para que no se borre de la barra
        'query': query, 
        'modalidad': modalidad
    }
    return render(request, 'aprendices/listar_aprendices.html', context)

# --- VISTA PARA EDITAR (UPDATE) ---
@login_required
def editar_aprendiz(request, pk):
    # 1. Buscamos el aprendiz por su id, si no existe sale error 404.
    aprendiz = get_object_or_404(Aprendiz, pk=pk)
    
    if request.method == 'POST':
        # 2. Cargamos SOLO el formulario del aprendiz con los nuevos datos
        # y le decimos qué "instance" (objeto) van a modificar
        form = AprendizForm(request.POST, instance=aprendiz)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'El perfil de aprendiz se ha actualizado correctamente.')
            return redirect('aprendices:listar_aprendices')
            
    else:
        # 3. Si es GET (apenas entramos a la página) cargamos el formulario lleno
        form = AprendizForm(instance=aprendiz)
    
    # 4. El contexto ahora es súper limpio y coincide con lo que espera el HTML
    context = {
        'form': form,      # La variable clave que le faltaba a tu vista
        'editar': True     # Banderita para cambiar el texto del botón y títulos
    }
    
    # Reutilizamos la misma plantilla
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

@login_required
def perfil_aprendiz(request):
    # 1. Seguridad: Verificamos si el usuario logueado es realmente un Aprendiz
    # Si entra un Admin o Instructor aquí, lo mandamos al home para evitar errores
    if not hasattr(request.user, 'aprendiz'):
        return redirect('core:home') 

    # 2. Obtenemos el perfil del aprendiz
    aprendiz = request.user.aprendiz
    
    # 3. Buscamos SUS bitácoras
    # CORRECCIÓN CLAVE: 
    # - Cambiamos 'numero' por 'numero_bitacora' (el campo nuevo)
    # - Ordenamos descendente (-) para que la bitácora 2 salga antes que la 1
    mis_bitacoras = Bitacora.objects.filter(aprendiz=aprendiz).order_by('-numero_bitacora')
    
    context = {
        'aprendiz': aprendiz,
        'bitacoras': mis_bitacoras # Pasamos la lista a la plantilla
    }
    return render(request, 'aprendices/perfil_aprendiz.html', context)
