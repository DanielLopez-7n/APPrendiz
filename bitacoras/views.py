from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from xhtml2pdf import pisa
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.template.loader import get_template


# Importamos Modelos y Formularios
from .models import Bitacora
from .forms import CrearBitacoraForm, ActividadFormSet
from core.models import Notificacion

@login_required
def listar_bitacoras(request):
    query = request.GET.get('q', '')
    
    # --- 1. LÓGICA DE AISLAMIENTO DE DATOS POR ROL ---
    if request.user.is_superuser:
        # Administrador global: Acceso total al histórico
        bitacoras_base = Bitacora.objects.all()
        
    elif hasattr(request.user, 'instructor'):
        # V5: Como el instructor ahora es un campo de texto, filtramos por su correo
        bitacoras_base = Bitacora.objects.filter(email_instructor_seguimiento=request.user.email)
        
    elif hasattr(request.user, 'aprendiz'):
        # V5: Corrección del nombre del campo y pasando directamente el ID
       bitacoras_base = Bitacora.objects.filter(aprendiz_rel=request.user.aprendiz)

        
    else:
        # Fallback de seguridad por si un usuario no tiene perfil asignado
        bitacoras_base = Bitacora.objects.none()

    # V5: Corrección del nombre del campo de fecha
    bitacoras_list = bitacoras_base.order_by('-fecha_entrega_bitacora')
    
    # --- 2. LÓGICA DE BÚSQUEDA ---
    if query:
        # V5: Buscamos directamente en las columnas de la nueva tabla (más rápido y sin errores)
        bitacoras_list = bitacoras_list.filter(
            Q(nombre_completo_aprendiz__icontains=query) |
            Q(numero_identificacion_aprendiz__icontains=query) |
            Q(numero_grupo_ficha__icontains=query) |
            Q(nombre_empresa__icontains=query)
        )
    
    # --- 3. PAGINACIÓN ---
    paginator = Paginator(bitacoras_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        # Se envían banderas booleanas al template para renderizado condicional si es necesario
        'es_aprendiz': hasattr(request.user, 'aprendiz'),
        'es_instructor': hasattr(request.user, 'instructor'),
    }
    return render(request, 'bitacoras/listar_bitacoras.html', context)


# --- VISTA: CREAR BITÁCORA ---

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
            # Tomamos el perfil correcto del aprendiz logueado
            aprendiz_usuario = request.user.aprendiz
            template_base = 'core/base_simple.html' 
            redirect_url = 'aprendices:perfil_aprendiz'
        except AttributeError:
            messages.error(request, 'No tienes permisos de Aprendiz.')
            return redirect('core:home') 

    if request.method == 'POST':
        # 1. Recibimos el Formulario Principal (CORREGIDO: Pasamos aprendiz_usuario)
        form = CrearBitacoraForm(request.POST, request.FILES, aprendiz=aprendiz_usuario)
        
        # 2. Recibimos el Formset (Las filas de actividades)
        formset = ActividadFormSet(request.POST, request.FILES, prefix='actividades')

        # 3. Validamos AMBOS
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # Guardar Bitácora
                    bitacora = form.save(commit=False)
                    if aprendiz_usuario:
                        # CORREGIDO: Usamos la nueva columna "aprendiz_rel"
                        bitacora.aprendiz_rel = aprendiz_usuario
                    bitacora.save()
                    
                    # Guardar Actividades vinculadas
                    formset.instance = bitacora
                    formset.save()

                    # --- CREAR NOTIFICACIÓN AL INSTRUCTOR ---
                    if bitacora.email_instructor_seguimiento:
                        try:
                            instructor_user = User.objects.get(email=bitacora.email_instructor_seguimiento)
                            nombre_aprendiz = bitacora.nombre_completo_aprendiz or request.user.get_full_name()
                            Notificacion.objects.create(
                                usuario_destino=instructor_user,
                                tipo='bitacora_nueva',
                                titulo='Nueva Bitácora Recibida',
                                mensaje=f'El aprendiz {nombre_aprendiz} ha subido la bitácora #{bitacora.numero_bitacora}.',
                                enlace=f'/bitacoras/revisar/{bitacora.id}/',
                            )
                        except User.DoesNotExist:
                            pass  # El instructor no existe en el sistema
                
                messages.success(request, '¡Formato GFPI-F-147 V5 guardado exitosamente!')
                return redirect(redirect_url)
            
            except Exception as e:
                messages.error(request, f'Error interno al guardar: {e}')
        else:
            # --- MAGIA PARA MOSTRAR ERRORES AL USUARIO ---
            
            # 1. Mostrar errores del formulario principal
            for campo, errores in form.errors.items():
                # Formatear el nombre del campo para que se vea más bonito (ej: nombre_empresa -> Nombre empresa)
                nombre_campo = campo.replace('_', ' ').capitalize()
                messages.error(request, f"Error en '{nombre_campo}': {errores[0]}")
                
            # 2. Mostrar errores de las actividades (Formset)
            for index, error_dict in enumerate(formset.errors):
                if error_dict:
                    for campo, errores in error_dict.items():
                        nombre_campo = campo.replace('_', ' ').capitalize()
                        messages.error(request, f"Error en la Actividad #{index + 1} ({nombre_campo}): {errores[0]}")
            
            messages.error(request, 'Por favor, revisa y corrige los campos indicados arriba.')
    else:
        # CORREGIDO: Usamos aprendiz_usuario para que no falle si entra un instructor a probar
        form = CrearBitacoraForm(aprendiz=aprendiz_usuario)
        formset = ActividadFormSet(prefix='actividades')

    context = {
        'form': form,
        'formset': formset,
        'titulo': "Nueva Bitácora V5",
        'template_to_extend': template_base,
        'es_instructor': es_instructor
    }
    return render(request, 'bitacoras/crear_bitacora.html', context)

# --- VISTA: EDITAR BITÁCORA (CORREGIDA PARA V5) ---
@login_required
def editar_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz_rel=request.user.aprendiz)

    if bitacora.estado != 'Pendiente':
        messages.error(request, "No puedes editar una bitácora evaluada.")
        return redirect('aprendices:perfil_aprendiz')

    if request.method == 'POST':
        form = CrearBitacoraForm(request.POST, request.FILES, instance=bitacora, aprendiz=request.user.aprendiz)
        formset = ActividadFormSet(request.POST, request.FILES, instance=bitacora, prefix='actividades')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Bitácora actualizada correctamente.")
            return redirect('aprendices:perfil_aprendiz')
    else:
        form = CrearBitacoraForm(instance=bitacora, aprendiz=request.user.aprendiz)
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
    bitacora = get_object_or_404(Bitacora, pk=pk, aprendiz_rel__usuario=request.user)

    return render(request, 'bitacoras/ver_bitacora_aprendiz.html', {'bitacora': bitacora})

# --- VISTA: VER DETALLE (INSTRUCTOR/ADMIN) ---
@login_required
def ver_bitacora(request, pk):
    bitacora = get_object_or_404(Bitacora, pk=pk)
    if hasattr(request.user, 'aprendiz') and bitacora.aprendiz_rel != request.user.aprendiz:

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
# ==============================================================================
# FUNCIÓN AUXILIAR: link_callback
# ==============================================================================
def link_callback(uri, rel):
    """
    Función crucial para xhtml2pdf. Convierte las URIs de Django (static, media)
    en rutas de archivo absolutas del sistema para que puedan ser incrustadas 
    correctamente en el PDF sin depender del servidor web.
    """
    # Usamos las configuraciones de Django para encontrar los directorios
    sUrl = settings.STATIC_URL      # Ejemplo: /static/
    sRoot = settings.STATIC_ROOT    # Ejemplo: /home/user/project/static/
    mUrl = settings.MEDIA_URL       # Ejemplo: /media/
    mRoot = settings.MEDIA_ROOT     # Ejemplo: /home/user/project/media/

    # Si la URI empieza con MEDIA_URL, buscamos en MEDIA_ROOT
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    # Si la URI empieza con STATIC_URL, buscamos en STATIC_ROOT
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    # Si no es ninguna de las anteriores, devolvemos la URI tal cual
    else:
        return uri

    # Verificamos que el archivo realmente exista en el disco
    if not os.path.isfile(path):
        # Si no existe, xhtml2pdf intentará descargarla (puede fallar)
        return uri
        
    return path


# ==============================================================================
# VISTA PRINCIPAL: exportar_pdf (Versión Profesional Limpia)
# ==============================================================================
@login_required
def exportar_pdf(request, pk):
    """
    Vista Senior: Genera un reporte PDF formal, aislado de la interfaz web,
    y soluciona el error 403 de permisos para aprendices.
    """
    bitacora = get_object_or_404(Bitacora, pk=pk)

    # --------------------------------------------------------------------------
    # CORRECCIÓN DE SEGURIDAD (Solución al error 403 Forbidden)
    # --------------------------------------------------------------------------
    # Obtenemos el usuario dueño de la bitácora de forma segura
    dueno_bitacora = bitacora.aprendiz_rel.usuario if bitacora.aprendiz_rel else None

    # Verificamos permisos:
    # 1. Si es superusuario o staff (instructor/admin), tiene acceso total.
    # 2. Si es el aprendiz dueño de la bitácora, tiene acceso.
    # 3. De lo contrario, se deniega el acceso.
    if not (request.user.is_superuser or request.user.is_staff or request.user == dueno_bitacora):
        # Esta es la alerta que le saldrá si intenta descargar algo que no es suyo
        messages.error(request, "Acceso denegado: No tienes permiso para exportar este documento.")
        return redirect('bitacoras:listar_bitacoras')

    # --------------------------------------------------------------------------
    # PREPARACIÓN DEL DOCUMENTO
    # --------------------------------------------------------------------------
    # Definimos el nombre dinámico del archivo PDF
    apellido = bitacora.aprendiz_rel.usuario.last_name if bitacora.aprendiz_rel else "Aprendiz"
    numero = getattr(bitacora, 'numero_bitacora', pk) # Usamos número si existe, sino el PK
    nombre_archivo = f"Reporte_Oficial_Bitacora_{numero}_{apellido}.pdf"

    # Ruta del template aislado (asegúrate de que este nombre coincida con el paso 2)
    template_path = 'bitacoras/reporte_bitacora_pdf.html'
    context = {'bitacora': bitacora}
    
    # Renderizamos el HTML de la plantilla con el contexto
    template = get_template(template_path)
    html = template.render(context)
    
    # Preparamos la respuesta HTTP para forzar la descarga
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    # --------------------------------------------------------------------------
    # GENERACIÓN DEL PDF (Inyectando link_callback)
    # --------------------------------------------------------------------------
    pisa_status = pisa.CreatePDF(
        html, 
        dest=response, 
        link_callback=link_callback # Crucial para logos e imágenes
    )
    
    # Verificamos si hubo errores durante la conversión
    if pisa_status.err:
        return HttpResponse('Error interno al renderizar el documento PDF.', status=500)
    
    return response


# --- VISTA: REVISAR BITÁCORA (CORREGIDA PARA V5) ---
def revisar_bitacora(request, id):
    bitacora = get_object_or_404(Bitacora, id=id)
    
    # Si el instructor le dio a "Guardar Calificación" en el modal
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones_instructor')

        # Manejo y validación de la firma (si fue enviada)
        firma_archivo = request.FILES.get('firma_instructor') if request.FILES else None
        if firma_archivo:
            # Validaciones básicas
            content_type = firma_archivo.content_type
            max_size = 2 * 1024 * 1024  # 2 MB
            if not content_type.startswith('image/'):
                messages.error(request, 'El archivo de firma debe ser una imagen válida.')
            elif firma_archivo.size > max_size:
                messages.error(request, 'La firma es demasiado grande. Máx. 2 MB.')
            else:
                try:
                    # Redimensionar para control de tamaño y aspecto
                    img = Image.open(firma_archivo)
                    img = img.convert('RGBA') if img.mode in ('P','LA','RGBA') else img.convert('RGB')
                    max_w, max_h = 800, 300
                    img.thumbnail((max_w, max_h), Image.LANCZOS)

                    buffer = io.BytesIO()
                    # Guardamos en PNG para mantener transparencia si existiera
                    img.save(buffer, format='PNG', optimize=True)
                    buffer.seek(0)

                    nombre = f'firma_bitacora_{bitacora.id}.png'
                    contenido = ContentFile(buffer.read())
                    # Asignamos pero no guardamos aún la instancia
                    bitacora.firma_instructor.save(nombre, contenido, save=False)
                except Exception as e:
                    messages.error(request, f'Error procesando la imagen de la firma: {e}')

        # Actualizamos y guardamos el resto de campos
        bitacora.estado = nuevo_estado
        bitacora.observaciones_instructor = observaciones
        bitacora.save()

        # --- CREAR NOTIFICACIÓN AL APRENDIZ ---
        if bitacora.aprendiz_rel and hasattr(bitacora.aprendiz_rel, 'usuario'):
            estado_msg = 'Aprobada ✅' if nuevo_estado == 'Evaluada' else 'Rechazada ❌'
            Notificacion.objects.create(
                usuario_destino=bitacora.aprendiz_rel.usuario,
                tipo='bitacora_evaluada',
                titulo=f'Bitácora #{bitacora.numero_bitacora} {estado_msg}',
                mensaje=f'Tu bitácora #{bitacora.numero_bitacora} ha sido {nuevo_estado.lower()} por el instructor.',
                enlace=f'/bitacoras/detalle/{bitacora.id}/',
            )
        
        messages.success(request, f'La Bitácora #{bitacora.numero_bitacora} fue calificada exitosamente.')
        return redirect('bitacoras:revisar_bitacora', id=bitacora.id)
    
    context = {'bitacora': bitacora}
    return render(request, 'bitacoras/revisar_bitacora.html', context)


# === API PARA AUTO-LLENADO DEL INSTRUCTOR ===
@login_required
def obtener_datos_instructor(request, instructor_id):
    """
    Recibe el ID de un instructor y devuelve su correo y teléfono en JSON
    para que el formulario (frontend) se llene automáticamente.
    """
    try:
        instructor = User.objects.get(id=instructor_id)
        email = instructor.email
        
        # Buscamos el teléfono (dependiendo de si está en su perfil de Instructor o en el Perfil general)
        telefono = ''
        if hasattr(instructor, 'instructor'):
            telefono = instructor.instructor.telefono
        elif hasattr(instructor, 'perfil'):
            telefono = instructor.perfil.telefono
            
        return JsonResponse({
            'success': True, 
            'email': email, 
            'telefono': telefono
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Instructor no encontrado'})
