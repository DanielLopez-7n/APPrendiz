from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
# from .utils import render_to_pdf # Asegúrate de que esta utilidad exista o coméntala si da error
from .models import Bitacora
from .forms import CrearBitacoraForm # Solo usamos este formulario nuevo

# --- VISTA: LISTAR BITÁCORAS ---
@login_required
def listar_bitacoras(request):
    # CASO 1: Aprendiz
    if hasattr(request.user, 'aprendiz'):
        bitacoras = Bitacora.objects.filter(aprendiz=request.user.aprendiz)
        es_aprendiz = True
    # CASO 2: Instructor o Admin
    elif request.user.is_staff:
        bitacoras = Bitacora.objects.all().order_by('-fecha_entrega')
        es_aprendiz = False
    else:
        bitacoras = []
        es_aprendiz = False

    context = {
        'bitacoras': bitacoras,
        'es_aprendiz': es_aprendiz,
        'titulo': 'Historial de Bitácoras'
    }
    return render(request, 'bitacoras/listar_bitacoras.html', context)

# --- VISTA: CREAR BITÁCORA (NUEVA LÓGICA V5) ---
@login_required
def crear_bitacora(request):
    # 1. DETERMINAR ROL
    es_instructor = request.user.is_staff
    
    if es_instructor:
        template_base = 'core/panel_admin_base.html'
        redirect_url = 'bitacoras:listar_bitacoras'
        titulo_pagina = "Registrar Bitácora (Admin)"
        aprendiz_usuario = None 
    else:
        try:
            aprendiz_usuario = request.user.aprendiz
            template_base = 'core/base_simple.html' # O la base de tu aprendiz
            redirect_url = 'aprendices:perfil_aprendiz' # Redirige al dashboard del aprendiz
            titulo_pagina = "Nueva Bitácora"
        except AttributeError:
            messages.error(request, 'No tienes permisos de Aprendiz para crear bitácoras.')
            return redirect('core:home') 

    # 2. PROCESAR FORMULARIO
    if request.method == 'POST':
        # Pasamos 'aprendiz' para validaciones si fuera necesario
        form = CrearBitacoraForm(request.POST, request.FILES, aprendiz=aprendiz_usuario)

        if form.is_valid():
            try:
                bitacora = form.save(commit=False)
                # Asignamos el aprendiz automáticamente
                if aprendiz_usuario:
                    bitacora.aprendiz = aprendiz_usuario
                
                bitacora.save()
                messages.success(request, '¡Bitácora guardada exitosamente!')
                return redirect(redirect_url)
            
            except Exception as e:
                messages.error(request, f'Error al guardar: {e}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        # GET: Pasamos el aprendiz para PRE-LLENAR datos (Empresa, Jefe, etc.)
        form = CrearBitacoraForm(aprendiz=aprendiz_usuario)

    context = {
        'form': form,
        'titulo': titulo_pagina,
        'template_to_extend': template_base,
        'es_instructor': es_instructor
    }
    return render(request, 'bitacoras/crear_bitacora.html', context)

# --- VISTA: VER DETALLE (ADMIN/INSTRUCTOR) ---
@login_required
def ver_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    # Seguridad básica
    if hasattr(request.user, 'aprendiz') and bitacora.aprendiz != request.user.aprendiz:
        messages.error(request, "No tienes permiso para ver esta bitácora.")
        return redirect('bitacoras:listar_bitacoras')

    context = {
        'bitacora': bitacora,
        'titulo': f'Detalle Bitácora #{bitacora.numero_bitacora}'
    }
    return render(request, 'bitacoras/ver_detalle.html', context)

# --- VISTA: VER DETALLE (APRENDIZ - LECTURA) ---
@login_required
def ver_bitacora_aprendiz(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz__usuario=request.user)
    return render(request, 'bitacoras/ver_bitacora_aprendiz.html', {
        'bitacora': bitacora
    })

# --- VISTA: REVISAR/EVALUAR (SOLO INSTRUCTORES) ---
@login_required
@user_passes_test(lambda u: u.is_staff)
def revisar_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    # Aquí deberías usar un Formulario de Evaluación si tienes uno específico
    # Si no, podrías procesar los campos 'estado' y 'observaciones' manualmente o crear un form simple
    if request.method == 'POST':
        estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones_instructor')
        
        if estado:
            bitacora.estado = estado
            bitacora.observaciones_instructor = observaciones
            bitacora.save()
            messages.success(request, f'Bitácora #{bitacora.numero_bitacora} evaluada.')
            return redirect('bitacoras:listar_bitacoras')
            
    context = {
        'bitacora': bitacora,
        'titulo': f'Revisar Bitácora - {bitacora.aprendiz}'
    }
    return render(request, 'bitacoras/revisar_bitacora.html', context)

# --- VISTA: EXPORTAR PDF ---
@login_required
def exportar_pdf(request, pk):
    # (Necesita ajuste para el nuevo modelo, lo dejo básico para que no falle)
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    if not request.user.is_staff and bitacora.aprendiz.usuario != request.user:
        messages.error(request, "No tienes permiso.")
        return redirect('core:home')

    # Simulamos render_to_pdf si no tienes la función importada
    return HttpResponse("Función de PDF pendiente de actualizar al nuevo formato V5.")