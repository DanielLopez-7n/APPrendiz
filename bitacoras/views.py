from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction # Para asegurar que se guarde todo o nada
from .models import Bitacora
from .forms import BitacoraForm, ActividadFormSet

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
        aprendiz_usuario = None # El instructor deberá elegir el aprendiz (si habilitamos eso luego)
    else:
        # Si es aprendiz, usa el diseño simple y redirige a su perfil
        try:
            aprendiz_usuario = request.user.aprendiz
            template_base = 'core/base_simple.html'
            # ASUMO que la URL de tu perfil es 'aprendices:perfil_aprendiz'. 
            # Si se llama diferente en tus urls.py, cámbialo aquí.
            redirect_url = 'aprendices:perfil_aprendiz' 
            titulo_pagina = "Nueva Bitácora"
        except AttributeError:
             # Caso raro: Usuario logueado pero sin perfil de aprendiz ni staff
             messages.error(request, 'No tienes permisos para crear bitácoras.')
             return redirect('home') # O a donde consideres

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

