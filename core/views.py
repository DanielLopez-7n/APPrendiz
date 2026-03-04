from django.shortcuts import render
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
    Reúne estadísticas de todas las apps.
    """
    # ==========================================
    # 1. ESTADÍSTICAS GENERALES (Las que ya tenías)
    # ==========================================
    total_aprendices = Aprendiz.objects.count()
    total_empresas = Empresa.objects.count()
    bitacoras_pendientes = Bitacora.objects.filter(estado='Pendiente').count()
    ultimas_bitacoras = Bitacora.objects.all().order_by('-fecha_entrega')[:5]

    total_fichas = Ficha.objects.count()
    total_programas = Programa.objects.count()

    # ==========================================
    # 2. ESTADÍSTICAS DE USUARIOS (Para las tarjetas y la tabla)
    # ==========================================
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()
    usuarios_staff = User.objects.filter(is_staff=True).count()
    
    # Usuarios nuevos registrados este mes
    hoy = timezone.now()
    nuevos_usuarios_mes = User.objects.filter(date_joined__year=hoy.year, date_joined__month=hoy.month).count()
    
    # Últimos 5 usuarios registrados (Para tu tabla de Registros Recientes)
    ultimos_usuarios = User.objects.all().order_by('-date_joined')[:5]

    # ==========================================
    # 3. DATOS PARA LOS GRÁFICOS (CHART.JS)
    # ==========================================
    
    # Gráfico 1: Estado de las Bitácoras (Dona)
    bitacoras_estado = Bitacora.objects.values('estado').annotate(total=Count('id'))
    labels_bitacoras = [item['estado'] for item in bitacoras_estado]
    data_bitacoras = [item['total'] for item in bitacoras_estado]
    
    # Gráfico 2: Distribución de Usuarios (Barras)
    total_admin = User.objects.filter(is_superuser=True).count()
    total_instructores = User.objects.filter(is_staff=True, is_superuser=False).count()
    total_solo_aprendices = User.objects.filter(is_staff=False, is_superuser=False).count()
    
    labels_usuarios = ['Administradores', 'Instructores', 'Aprendices']
    data_usuarios = [total_admin, total_instructores, total_solo_aprendices]

    # ==========================================
    # 4. EMPAQUETAR Y ENVIAR AL TEMPLATE
    # ==========================================
    context = {
        'titulo': 'Panel de Control',
        
        # Datos extraídos (los tuyos originales)
        'total_aprendices': total_aprendices,
        'total_empresas': total_empresas,
        'bitacoras_pendientes': bitacoras_pendientes,
        'ultimas_bitacoras': ultimas_bitacoras,
        'total_fichas': total_fichas,
        'total_programas': total_programas,
        
        # Datos vitales para el HTML del Dashboard actual
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_staff': usuarios_staff,
        'nuevos_usuarios_mes': nuevos_usuarios_mes,
        'ultimos_usuarios': ultimos_usuarios,
        
        # Listas de Python convertidas a formato JSON para JavaScript
        'labels_bitacoras': json.dumps(labels_bitacoras),
        'data_bitacoras': json.dumps(data_bitacoras),
        'labels_usuarios': json.dumps(labels_usuarios),
        'data_usuarios': json.dumps(data_usuarios),
    }
    
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
    
    # Inicializamos listas vacías
    aprendices = []
    instructores = []
    empresas = []
    usuarios = [] 

    if query:
        # 1. Búsqueda Aprendices
        aprendices = Aprendiz.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |
            Q(documento__icontains=query)
            # Descomentaremos estas cuando sepamos el nombre exacto de los campos en Ficha y Programa
            # | Q(programa_formacion__nombre__icontains=query) 
            # | Q(numero_ficha__numero_ficha__icontains=query) 
        ).distinct()

        # 2. Búsqueda Instructores
        instructores = Instructor.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |          
            Q(profesion__icontains=query)
        ).distinct()

        # 3. Búsqueda Empresas (¡Corregido a 'nombre'!)
        empresas = Empresa.objects.filter(
            Q(nombre__icontains=query) | 
            Q(nit__icontains=query)
        ).distinct()
        
        # 4. Búsqueda Usuarios (General)
        usuarios = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).distinct()

    # Calculamos el total sumando las 4 listas
    total = len(aprendices) + len(instructores) + len(empresas) + len(usuarios)

    context = {
        'query': query,
        'aprendices': aprendices,
        'instructores': instructores,
        'empresas': empresas,
        'usuarios': usuarios,  
        'total_resultados': total,
        'titulo': 'Resultados de Búsqueda'
    }
    
    return render(request, 'core/resultados_busqueda.html', context)

# --- VISTA DE LOGIN PERSONALIZADA ---

class CustomLoginView(LoginView):
    template_name = 'core/index.html' 
    
    def form_valid(self, form):
        # Capturamos si el usuario marcó el checkbox (devuelve 'on' si está marcado, o None si no)
        remember_me = self.request.POST.get('remember_me')
        
        if not remember_me:
            # Si NO la marcó, la sesión caduca al cerrar el navegador (0 segundos)
            self.request.session.set_expiry(0)
        else:
            # Si SÍ la marcó, la sesión dura 2 semanas (1209600 segundos)
            self.request.session.set_expiry(1209600)
            
        return super().form_valid(form)