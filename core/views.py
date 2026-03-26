from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.models import User 
from fichas.models import Ficha
from programas.models import Programa
from django.contrib.auth.views import LoginView
from bitacoras.models import Bitacora
from django.db.models import Count
import json
from django.utils import timezone


# Importamos los modelos de nuestras Apps para las estadísticas
from aprendices.models import Aprendiz
from empresas.models import Empresa
from bitacoras.models import Bitacora
from instructores.models import Instructor

def index(request):
    """Vista de la página de inicio (Landing Page)"""
    return render(request, 'core/index.html')

def nosotros(request):
    return render(request, 'core/nosotros.html')

def contactanos(request):
    return render(request, 'core/contactanos.html')

# --- VISTAS ADMINISTRATIVAS ---

@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    """
    Vista principal del panel de administración (Dashboard).
    Muestra gráficas de Usuarios al Administrador y gráficas de Bitácoras al Instructor.
    """
    user = request.user
    hoy = timezone.now()
    
    # 1. ¿Quién está entrando? (Lógica "Bipolar")
    es_admin = user.is_superuser or (user.is_staff and not hasattr(user, 'instructor'))
    
    # 2. Alerta de Contraseña (Seguridad)
    alerta_password = False
    if not user.is_superuser:
        alerta_password = user.check_password(user.username)
        
    # 3. Empaquetamos los datos BASE que comparten ambos
    context = {
        'titulo': 'Panel de Control',
        'es_admin': es_admin,
        'alerta_password': alerta_password,
    }

    if es_admin:
        # ==========================================
        # 🟢 LÓGICA PARA EL ADMINISTRADOR
        # ==========================================
        # Tarjetas Superiores
        total_usuarios = User.objects.count()
        usuarios_activos = User.objects.filter(is_active=True).count()
        total_aprendices = Aprendiz.objects.count()
        total_instructores = User.objects.filter(is_staff=True, is_superuser=False).count()
        ultimos_usuarios = User.objects.all().order_by('-date_joined')[:5]
        
        # Agregamos los datos al contexto usando .update() para no borrar lo anterior
        context.update({
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'total_aprendices': total_aprendices,
            'total_instructores': total_instructores,
            # Mantenemos las tuyas por si las necesitas en otra parte:
            'total_empresas': Empresa.objects.count() if 'Empresa' in globals() else 0,
            'total_fichas': Ficha.objects.count() if 'Ficha' in globals() else 0,
            'total_programas': Programa.objects.count() if 'Programa' in globals() else 0,
            'ultimos_usuarios': ultimos_usuarios,
        })
        
        # Datos para Gráfica de Admin (Distribución de Usuarios)
        labels_usuarios = ['Administradores', 'Instructores', 'Aprendices']
        data_usuarios = [
            User.objects.filter(is_superuser=True).count(),
            total_instructores,
            total_aprendices
        ]
        context['chart_labels'] = json.dumps(labels_usuarios)
        context['chart_data'] = json.dumps(data_usuarios)

    else:
        # ==========================================
        # 🟠 LÓGICA PARA EL INSTRUCTOR
        # ==========================================
        try:
            # 🔥 LA SOLUCIÓN: Comparamos el correo que guardó la bitácora con el correo del instructor que inició sesión
            pendientes = Bitacora.objects.filter(email_instructor_seguimiento=user.email, estado='Pendiente').count()
            evaluadas = Bitacora.objects.filter(email_instructor_seguimiento=user.email, estado='Evaluada').count()
            rechazadas = Bitacora.objects.filter(email_instructor_seguimiento=user.email, estado='Rechazada').count()
            
            context.update({
                'pendientes': pendientes,
                'evaluadas': evaluadas,
                'total_bitacoras': pendientes + evaluadas + rechazadas,
            })
            
            # Datos para Gráfica de Instructor (Estado de sus Bitácoras)
            context['chart_labels'] = json.dumps(['Pendientes', 'Evaluadas', 'Rechazadas'])
            context['chart_data'] = json.dumps([pendientes, evaluadas, rechazadas])
            
        except Exception as e:
            print(f"👉 ERROR EN DASHBOARD INSTRUCTOR: {e}") 
            
            context.update({'pendientes': 0, 'evaluadas': 0, 'total_bitacoras': 0})
            context['chart_labels'] = json.dumps(['Sin datos'])
            context['chart_data'] = json.dumps([0])

    # Enviamos el paquete completo de forma segura
    return render(request, 'core/dashboard.html', context)

# --- VISTAS UTILITARIAS ---

def search(request):
    return render(request, 'core/search.html')

def help_page(request):
    return render(request, 'core/help.html')

def PanelAdmin_base(request):
    """Vista temporal para ver el diseño base (opcional)"""
    return render(request, 'core/panel_admin_base.html')


# --- VISTA DE BÚSQUEDA GLOBAL ---

@login_required
def busqueda_global(request):
    query = request.GET.get('q', '').strip()
    
    # Inicializamos todas las listas
    aprendices = []
    instructores = []
    empresas = []
    bitacoras = []
    bitacoras_por_aprendiz = []
    fichas = []
    programas = []

    if query:
        # 1. Aprendices (Buscamos por nombre, apellido, documento o ficha)
        aprendices = Aprendiz.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |
            Q(documento__icontains=query) |
            Q(numero_ficha__numero__icontains=query)
        ).distinct()

        # 2. Instructores (Nombre, apellido, profesión o documento)
        instructores = Instructor.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |          
            Q(cedula__icontains=query) |
            Q(profesion__icontains=query)
        ).distinct()

        # 3. Empresas (Nombre o NIT)
        empresas = Empresa.objects.filter(
            Q(nombre__icontains=query) | 
            Q(nit__icontains=query)
        ).distinct()
        
        # 4. Bitácoras (Por nombre del aprendiz, ID, o estado)
        bitacoras = Bitacora.objects.filter(
            Q(nombre_completo_aprendiz__icontains=query) |
            Q(numero_identificacion_aprendiz__icontains=query) |
            Q(estado__icontains=query) |
            Q(email_instructor_seguimiento__icontains=query)
        ).order_by('-id').distinct()[:15] # Limitamos a las 15 más recientes para no saturar

        # 4.1 Resumen por aprendiz: cuántas bitácoras ha entregado
        aprendices_ids = list(aprendices.values_list('id', flat=True))
        if aprendices_ids:
            conteos = (
                Bitacora.objects
                .filter(aprendiz_rel_id__in=aprendices_ids)
                .values('aprendiz_rel_id')
                .annotate(total=Count('id'))
            )
            conteos_map = {item['aprendiz_rel_id']: item['total'] for item in conteos}

            for aprendiz in aprendices:
                aprendiz.total_bitacoras = conteos_map.get(aprendiz.id, 0)
                if aprendiz.total_bitacoras > 0:
                    bitacoras_por_aprendiz.append(aprendiz)

        # 5. Fichas y Programas
        fichas = Ficha.objects.filter(Q(numero__icontains=query)).distinct()
        programas = Programa.objects.filter(Q(nombre__icontains=query)).distinct()

    # Calculamos el total de todo lo encontrado
    total = (len(aprendices) + len(instructores) + len(empresas) + 
             len(bitacoras_por_aprendiz) + len(fichas) + len(programas))

    context = {
        'query': query,
        'aprendices': aprendices,
        'instructores': instructores,
        'empresas': empresas,
        'bitacoras': bitacoras,
        'bitacoras_por_aprendiz': bitacoras_por_aprendiz,
        'fichas': fichas,
        'programas': programas,
        'total_resultados': total,
        'titulo': f'Resultados para: {query}'
    }
    
    return render(request, 'core/resultados_busqueda.html', context)

# --- VISTA DE LOGIN PERSONALIZADA ---

class CustomLoginView(LoginView):
    # plantilla usada por defecto al POST exitoso; para GET redirigimos al index
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        # Si el usuario visita directamente la URL de login, redirigimos al index
        return redirect('core:index')

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(1209600)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Cuando las credenciales son inválidas, mostramos la vista completa de login
        context = self.get_context_data(form=form)
        # renderizamos la plantilla dedicada donde el usuario puede corregir credenciales
        return render(self.request, 'usuarios/login.html', context, status=401)


# --- VISTAS DE NOTIFICACIONES ---

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notificacion


@login_required
@require_POST
def marcar_notificacion_leida(request, pk):
    """Marca una notificación como leída y redirige a su enlace."""
    try:
        notificacion = Notificacion.objects.get(pk=pk, usuario_destino=request.user)
        notificacion.leida = True
        notificacion.save()
        
        # Si tiene enlace, redirigimos ahí; si no, al dashboard
        if notificacion.enlace:
            return redirect(notificacion.enlace)
        return redirect('core:dashboard')
    except Notificacion.DoesNotExist:
        return redirect('core:dashboard')


@login_required
@require_POST
def marcar_todas_leidas(request):
    """Marca todas las notificaciones del usuario como leídas (AJAX)."""
    Notificacion.objects.filter(
        usuario_destino=request.user,
        leida=False
    ).update(leida=True)
    
    return JsonResponse({'success': True, 'message': 'Todas las notificaciones marcadas como leídas.'})


@login_required
def obtener_notificaciones(request):
    """Devuelve las notificaciones no leídas en formato JSON para polling AJAX."""
    notificaciones = Notificacion.objects.filter(
        usuario_destino=request.user,
        leida=False
    ).order_by('-fecha_creacion')[:10]

    data = []
    for n in notificaciones:
        # Calcular tiempo relativo
        from django.utils.timesince import timesince
        tiempo = timesince(n.fecha_creacion, timezone.now())
        # Tomar solo la primera parte (ej: "2 horas" en vez de "2 horas, 3 minutos")
        tiempo_corto = tiempo.split(',')[0]

        data.append({
            'id': n.id,
            'tipo': n.tipo,
            'titulo': n.titulo,
            'mensaje': n.mensaje,
            'enlace': n.enlace or '',
            'tiempo': f'Hace {tiempo_corto}',
        })

    total = Notificacion.objects.filter(
        usuario_destino=request.user,
        leida=False
    ).count()

    return JsonResponse({'notificaciones': data, 'total': total})


# ==========================================
# MÓDULO DE COPIAS DE SEGURIDAD (BACKUPS)
# ==========================================
import os
import zipfile
from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib import messages
from datetime import datetime

# Función auxiliar para comprobar superusuario
def es_superusuario(user):
    return user.is_active and user.is_superuser

@login_required
@user_passes_test(es_superusuario)
def listar_backups(request):
    """Muestra el historial de backups generados"""
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    # Crear directorio si no existe
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
        
    archivos = []
    for f in os.listdir(backups_dir):
        if f.endswith('.zip'):
            filepath = os.path.join(backups_dir, f)
            stats = os.stat(filepath)
            archivos.append({
                'nombre': f,
                'tamano_mb': round(stats.st_size / (1024 * 1024), 2),
                'fecha_creacion': datetime.fromtimestamp(stats.st_ctime)
            })
            
    # Ordenar del más reciente al más antiguo
    archivos.sort(key=lambda x: x['fecha_creacion'], reverse=True)
    
    return render(request, 'core/backups.html', {'archivos': archivos})


@login_required
@user_passes_test(es_superusuario)
def crear_backup(request):
    """Genera un archivo ZIP conteniendo la Base de Datos y la carpeta Media"""
    try:
        backups_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backups_dir):
            os.makedirs(backups_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'backup_sena_{timestamp}.zip'
        zip_filepath = os.path.join(backups_dir, zip_filename)
        
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        media_path = settings.MEDIA_ROOT
        
        # Comprimir
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Base de datos
            if os.path.exists(db_path):
                zipf.write(db_path, os.path.basename(db_path))
                
            # 2. Archivos Multimedia (firmas, fotos, anexos)
            if os.path.exists(media_path):
                for root, dirs, files in os.walk(media_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calcula la ruta relativa para no guardar toda la ruta completa C:\ en el zip
                        arcname = os.path.relpath(file_path, settings.BASE_DIR)
                        zipf.write(file_path, arcname)
                        
        messages.success(request, f'Backup generado exitosamente: {zip_filename}')
    except Exception as e:
        messages.error(request, f'Error al generar copias de seguridad: {str(e)}')
        
    return redirect('core:listar_backups')


@login_required
@user_passes_test(es_superusuario)
def descargar_backup(request, nombre_archivo):
    """Permite al administrador descargar el backup a su PC"""
    # Seguridad básica para evitar ataques "Directory Traversal"
    if '..' in nombre_archivo or not nombre_archivo.endswith('.zip'):
        raise Http404("Archivo no permitido")
        
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backups_dir, nombre_archivo)
    
    if os.path.exists(filepath):
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=nombre_archivo)
        return response
    else:
        messages.error(request, 'El archivo solicitado ya no existe.')
        return redirect('core:listar_backups')


@login_required
@user_passes_test(es_superusuario)
def eliminar_backup(request, nombre_archivo):
    """Elimina el archivo del historial"""
    if '..' in nombre_archivo or not nombre_archivo.endswith('.zip'):
        raise Http404("Archivo no permitido")
        
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backups_dir, nombre_archivo)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            messages.success(request, f'Archivo devuelto: {nombre_archivo} eliminado.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el archivo: {e}')
    else:
        messages.warning(request, 'El archivo no fue encontrado.')
        
    return redirect('core:listar_backups')
