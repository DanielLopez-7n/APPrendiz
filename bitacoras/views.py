from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction

# Importamos Modelos y Formularios
from .models import Bitacora
from .forms import CrearBitacoraForm, ActividadFormSet

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

# --- VISTA: CREAR BITÁCORA (CORREGIDA PARA V5) ---
@login_required
def crear_bitacora(request):
    # Validar que sea aprendiz (o instructor admin)
    es_instructor = request.user.is_staff
    
    if es_instructor:
        template_base = 'core/panel_admin_base.html'
        redirect_url = 'bitacoras:listar_bitacoras'
        aprendiz_usuario = None 
    else:
        try:
            aprendiz_usuario = request.user.aprendiz
            template_base = 'core/base_simple.html' 
            redirect_url = 'aprendices:perfil_aprendiz'
        except AttributeError:
            messages.error(request, 'No tienes permisos de Aprendiz.')
            return redirect('core:home') 

    if request.method == 'POST':
        # 1. Recibimos el Formulario Principal
        form = CrearBitacoraForm(request.POST, request.FILES, user=request.user)
        
        # 2. Recibimos el Formset (Las filas de actividades)
        formset = ActividadFormSet(request.POST, request.FILES, prefix='actividades')

        # 3. Validamos AMBOS
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar Bitácora
                    bitacora = form.save(commit=False)
                    if aprendiz_usuario:
                        bitacora.aprendiz = aprendiz_usuario
                    bitacora.save()
                    
                    # Guardar Actividades vinculadas
                    formset.instance = bitacora
                    formset.save()
                
                messages.success(request, '¡Bitácora guardada exitosamente!')
                return redirect(redirect_url)
            
            except Exception as e:
                messages.error(request, f'Error al guardar: {e}')
        else:
            # AQUÍ ESTÁ LA TRAMPA PARA VER EL ERROR REAL EN LA TERMINAL:
            print("--- ERRORES DETECTADOS ---")
            print("Errores de la Bitácora:", form.errors)
            print("Errores de las Actividades:", formset.errors)
            
            messages.error(request, 'Hay errores en el formulario. Revisa los campos en rojo.')
    else:
        form = CrearBitacoraForm(user=request.user)
        formset = ActividadFormSet(prefix='actividades')

    context = {
        'form': form,
        'formset': formset,
        'titulo': "Nueva Bitácora",
        'template_to_extend': template_base,
        'es_instructor': es_instructor
    }
    return render(request, 'bitacoras/crear_bitacora.html', context)

# --- VISTA: EDITAR BITÁCORA (CORREGIDA PARA V5) ---
@login_required
def editar_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz=request.user.aprendiz)

    if bitacora.estado != 'Pendiente':
        messages.error(request, "No puedes editar una bitácora evaluada.")
        return redirect('aprendices:perfil_aprendiz')

    if request.method == 'POST':
        form = CrearBitacoraForm(request.POST, request.FILES, instance=bitacora, user=request.user)
        formset = ActividadFormSet(request.POST, request.FILES, instance=bitacora, prefix='actividades')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Bitácora actualizada correctamente.")
            return redirect('aprendices:perfil_aprendiz')
    else:
        form = CrearBitacoraForm(instance=bitacora, user=request.user)
        formset = ActividadFormSet(instance=bitacora, prefix='actividades')

    context = {
        'form': form,
        'formset': formset,
        'titulo': f'Editar Bitácora N° {bitacora.numero_bitacora}',
        'template_to_extend': 'core/base_simple.html'
    }
    return render(request, 'bitacoras/crear_bitacora.html', context)

# --- VISTA: ELIMINAR BITÁCORA ---
@login_required
def eliminar_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz=request.user.aprendiz)
    
    if bitacora.estado == 'Pendiente':
        bitacora.delete()
        messages.success(request, "Bitácora eliminada correctamente.")
    else:
        messages.error(request, "No se puede eliminar una bitácora evaluada.")
        
    return redirect('aprendices:perfil_aprendiz')

# --- VISTA: VER DETALLE (APRENDIZ) ---
@login_required
def ver_bitacora_aprendiz(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz__usuario=request.user)
    return render(request, 'bitacoras/ver_bitacora_aprendiz.html', {'bitacora': bitacora})

# --- VISTA: VER DETALLE (INSTRUCTOR/ADMIN) ---
@login_required
def ver_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk)
    if hasattr(request.user, 'aprendiz') and bitacora.aprendiz != request.user.aprendiz:
        messages.error(request, "No tienes permiso para ver esta bitácora.")
        return redirect('bitacoras:listar_bitacoras')
    
    return render(request, 'bitacoras/ver_bitacora_aprendiz.html', {'bitacora': bitacora})
    
# --- VISTA: REVISAR BITÁCORA (SOLO INSTRUCTOR) ---
@login_required
def revisar_bitacora(request, pk):
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para revisar bitácoras.")
        return redirect('bitacoras:listar_bitacoras')

    bitacora = get_object_or_404(Bitacora, pk=pk)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones_instructor')

        if nuevo_estado:
            bitacora.estado = nuevo_estado
            bitacora.observaciones_instructor = observaciones
            bitacora.save()
            
            messages.success(request, f"La Bitácora N° {bitacora.numero_bitacora} ha sido marcada como {nuevo_estado}.")
            return redirect('bitacoras:listar_bitacoras')

    context = {
        'bitacora': bitacora,
        'titulo': f'Revisar Bitácora N° {bitacora.numero_bitacora}',
        'template_to_extend': 'core/panel_admin_base.html' 
    }
    return render(request, 'bitacoras/revisar_bitacora.html', context)

# --- VISTA: EXPORTAR PDF ---
@login_required
def exportar_pdf(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk)
    
    es_dueno = hasattr(request.user, 'aprendiz') and bitacora.aprendiz == request.user.aprendiz
    es_instructor = request.user.is_staff
    
    if not es_dueno and not es_instructor:
        messages.error(request, "No tienes permiso para descargar esta bitácora.")
        return redirect('core:home')

    return HttpResponse("Función de PDF pendiente de actualizar al nuevo formato V5.")