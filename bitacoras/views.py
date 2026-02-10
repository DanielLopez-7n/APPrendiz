from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from .models import Bitacora
from .forms import BitacoraForm, ActividadFormSet
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import render_to_pdf
# Importar para la evaluación
from .models import Bitacora
from .forms import BitacoraForm, ActividadFormSet, EvaluacionBitacoraForm

@login_required
def listar_bitacoras(request):
    # Lógica inteligente: ¿Quién eres?
    
    # CASO 1: Eres un Aprendiz
    if hasattr(request.user, 'aprendiz'):
        # Solo te muestro TUS bitácoras
        bitacoras = Bitacora.objects.filter(aprendiz=request.user.aprendiz)
        es_aprendiz = True
    
    # CASO 2: Eres Instructor o Admin
    elif request.user.is_staff:
        # Te muestro TODAS las bitácoras del sistema
        bitacoras = Bitacora.objects.all()
        es_aprendiz = False
    
    # CASO 3: Usuario raro (ni aprendiz ni staff)
    else:
        bitacoras = []
        es_aprendiz = False

    context = {
        'bitacoras': bitacoras,
        'es_aprendiz': es_aprendiz,
        'titulo': 'Historial de Bitácoras'
    }
    return render(request, 'bitacoras/listar_bitacoras.html', context)

@login_required
def crear_bitacora(request):
    # 1. DETERMINAR EL ROL Y CONFIGURAR EL ENTORNO
    es_instructor = request.user.is_staff
    
    if es_instructor:
        # Si es instructor, usa el diseño del Dashboard y redirige a la lista general
        template_base = 'core/panel_admin_base.html'
        redirect_url = 'bitacoras:listar_bitacoras'
        titulo_pagina = "Registrar Bitácora (Admin)"
        aprendiz_usuario = None 
    else:
        try:
            aprendiz_usuario = request.user.aprendiz
            template_base = 'core/base_simple.html'
            redirect_url = 'aprendices:perfil_aprendiz' 
            titulo_pagina = "Nueva Bitácora"
        except AttributeError:
             # Caso raro: Usuario logueado pero sin perfil de aprendiz ni staff
             messages.error(request, 'No tienes permisos para crear bitácoras.')
             return redirect('home') 

    # 2. PROCESAR EL FORMULARIO
    if request.method == 'POST':
        form = BitacoraForm(request.POST)
        formset = ActividadFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    bitacora = form.save(commit=False)
                    # Si es aprendiz, se asigna automáticamente.
                    if aprendiz_usuario:
                        bitacora.aprendiz = aprendiz_usuario
                    # NOTA: Si fuera instructor creando, aquí faltaría lógica para asignar el aprendiz.
                    # Por ahora asumimos que solo el aprendiz crea la suya.
                    
                    bitacora.save()
                    formset.instance = bitacora
                    formset.save()

                messages.success(request, '¡Bitácora creada exitosamente!')
                # Redirección dinámica según el rol
                return redirect(redirect_url)
            
            except Exception as e:
                messages.error(request, f'Error al guardar: {e}')
        else:
             messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BitacoraForm()
        formset = ActividadFormSet()

    # 3. ENVIAR CONTEXTO AL TEMPLATE
    context = {
        'form': form,
        'formset': formset,
        'titulo': titulo_pagina,
        # Pasamos la variable que decide qué diseño usar
        'template_to_extend': template_base,
        'es_instructor': es_instructor # Para usarlo en el botón "Cancelar"
    }
    return render(request, 'bitacoras/crear_bitacora.html', context)

@login_required
def ver_bitacora(request, pk):
    # Buscamos la bitácora y sus actividades
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    # Seguridad: Si es aprendiz, solo puede ver la suya
    if hasattr(request.user, 'aprendiz') and bitacora.aprendiz != request.user.aprendiz:
        messages.error(request, "No tienes permiso para ver esta bitácora.")
        return redirect('bitacoras:listar_bitacoras')

    context = {
        'bitacora': bitacora,
        'titulo': f'Detalle Bitácora #{bitacora.numero}'
    }
    return render(request, 'bitacoras/ver_detalle.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff) # Solo para instructores/admin
def revisar_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    if request.method == 'POST':
        form = EvaluacionBitacoraForm(request.POST, instance=bitacora)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bitácora #{bitacora.numero} evaluada correctamente.')
            return redirect('bitacoras:listar_bitacoras')
    else:
        form = EvaluacionBitacoraForm(instance=bitacora)

    context = {
        'bitacora': bitacora,
        'form': form,
        'titulo': f'Revisar Bitácora - {bitacora.aprendiz}'
    }
    return render(request, 'bitacoras/revisar_bitacora.html', context)

# Generar PDF de la bitácora

@login_required
def exportar_pdf(request, pk):
    """
    Genera el reporte PDF de una bitácora específica
    """
    # 1. Buscamos la bitácora (asegurando que sea del usuario o que sea staff)
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    # Seguridad básica: Solo el dueño o un instructor puede descargarla
    if not request.user.is_staff and bitacora.aprendiz.usuario != request.user:
        messages.error(request, "No tienes permiso para ver este documento.")
        return redirect('core:index')

    # 2. Preparamos los datos para el reporte
    context = {
        'bitacora': bitacora,
        'aprendiz': bitacora.aprendiz,
        'empresa': bitacora.empresa,
        'actividades': bitacora.actividades.all(),
        'request': request # Útil si necesitamos construir URLs absolutas
    }
    
    # 3. Generamos el PDF usando el template específico
    pdf = render_to_pdf('bitacoras/pdf_template.html', context)
    
    if pdf:
        # Esto hace que el navegador lo muestre en lugar de descargarlo directo
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Bitacora_{bitacora.numero}_{bitacora.aprendiz.usuario.username}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
        
    return HttpResponse("Error al generar el PDF", status=404)

@login_required
def ver_bitacora_aprendiz(request, pk):
    # 1. Buscamos la bitácora, PERO aseguramos que pertenezca al usuario logueado
    # El filtro 'aprendiz__usuario=request.user' es el candado de seguridad
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz__usuario=request.user)
    
    return render(request, 'bitacoras/ver_bitacora_aprendiz.html', {
        'bitacora': bitacora
    })
    