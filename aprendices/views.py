from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AprendizForm
from .models import Aprendiz
from django.shortcuts import get_object_or_404
from bitacoras.models import Bitacora
from django.db.models import Q
from .models import Aprendiz
from usuarios.forms import AprendizPerfilForm

# Vista para Listar todos los Aprendices
@login_required
def listar_aprendices(request):
    aprendices = Aprendiz.objects.select_related('usuario', 'numero_ficha')
    
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

    # Mostrar primero los registros más recientes
    aprendices = aprendices.order_by('-usuario__date_joined', '-id')

    context = {
        'aprendices': aprendices,
        # Opcional: mandamos la query de vuelta para que no se borre de la barra
        'query': query, 
        'modalidad': modalidad
    }
    return render(request, 'aprendices/listar_aprendices.html', context)

# --- VISTA PARA EDITAR (UPDATE ADMINISTRADOR) ---
@login_required
def editar_aprendiz(request, pk):
    # 1. Buscamos el aprendiz por su id, si no existe sale error 404.
    aprendiz = get_object_or_404(Aprendiz, pk=pk)
    
    if request.method == 'POST':
        # 2. Cargamos SOLO el formulario del aprendiz con los nuevos datos
        form = AprendizForm(request.POST, instance=aprendiz)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'El perfil de aprendiz se ha actualizado correctamente.')
            return redirect('aprendices:listar_aprendices')
            
    else:
        # 3. Si es GET (apenas entramos a la página) cargamos el formulario lleno
        form = AprendizForm(instance=aprendiz)
    
    context = {
        'form': form,      
        'editar': True     
    }
    
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
    bitacoras_entregadas = Bitacora.objects.filter(aprendiz_rel=aprendiz).count()
    context = {
        'aprendiz': aprendiz,
        'bitacoras_entregadas': bitacoras_entregadas,
    }
    return render(request, 'aprendices/ver_detalle.html', context)


# --- VISTA PARA EL PERFIL DEL APRENDIZ (CON SUS BITÁCORAS) ---

@login_required
def perfil_aprendiz(request):
    # 1. Seguridad: Verificamos si el usuario logueado es realmente un Aprendiz
    if not hasattr(request.user, 'aprendiz'):
        return redirect('core:dashboard')  

    # 2. Obtenemos el perfil del aprendiz
    aprendiz = request.user.aprendiz
    
    # 3. Buscamos SUS bitácoras
    # ¡CORRECCIÓN APLICADA AQUÍ!: Cambiamos 'aprendiz' por 'aprendiz_rel'
    mis_bitacoras = Bitacora.objects.filter(aprendiz_rel=aprendiz).order_by('-numero_bitacora')
    
    # 4. Contamos las pendientes
    bitacoras_pendientes_count = mis_bitacoras.filter(estado='Pendiente').count()
    
    alerta_password = request.user.check_password(request.user.username)
    context = {
        'aprendiz': aprendiz,
        'bitacoras': mis_bitacoras,
        'bitacoras_pendientes_count': bitacoras_pendientes_count,
        'alerta_password': alerta_password
    }
    return render(request, 'aprendices/perfil_aprendiz.html', context)

# --- VISTA PARA EDITAR PERFIL ---

@login_required
def editar_perfil_aprendiz(request):
    # Buscamos el registro de aprendiz que pertenece a este usuario
    try:
        aprendiz = Aprendiz.objects.get(usuario=request.user)
    except Aprendiz.DoesNotExist:
        messages.error(request, "No se encontró un perfil de aprendiz asociado.")
        return redirect('core:dashboard')

    if request.method == 'POST':
        # Le pasamos la información actual (instance) y el usuario para que sincronice ambos
        form = AprendizPerfilForm(request.POST, request.FILES, instance=aprendiz, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu información se ha actualizado y sincronizado correctamente!')
            return redirect('aprendices:perfil_aprendiz')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = AprendizPerfilForm(instance=aprendiz, user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'aprendices/editar_perfil.html', context)
