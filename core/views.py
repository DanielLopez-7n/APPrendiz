from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.models import User # <--- Importante


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
    # 1. Estadísticas de APPRENDIZ
    total_aprendices = Aprendiz.objects.count()
    total_empresas = Empresa.objects.count()
    
    # --- CORRECCIÓN 1: Usamos el campo 'estado' para saber cuáles faltan ---
    # Antes buscabas 'instructor_seguimiento=False', ahora es por estado:
    bitacoras_pendientes = Bitacora.objects.filter(estado='Pendiente').count()
    
    # --- CORRECCIÓN 2: Usamos 'fecha_entrega' para ordenar ---
    # 'fecha_creacion' ya no existe en el modelo V5
    ultimas_bitacoras = Bitacora.objects.all().order_by('-fecha_entrega')[:5]

    # 2. Estadísticas de Usuarios
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()

    context = {
        'titulo': 'Panel de Control',
        'total_aprendices': total_aprendices,
        'total_empresas': total_empresas,
        'bitacoras_pendientes': bitacoras_pendientes,
        'ultimas_bitacoras': ultimas_bitacoras,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
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
    query = request.GET.get('q')
    
    # Inicializamos listas vacías
    aprendices = []
    instructores = []
    empresas = []
    usuarios = [] # <--- Lista nueva

    if query:
        # 1. Búsqueda Aprendices
        aprendices = Aprendiz.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |
            Q(programa_formacion__icontains=query) |
            Q(numero_ficha__icontains=query)
        ).distinct()

        # 2. Búsqueda Instructores
        instructores = Instructor.objects.filter(
            Q(usuario__first_name__icontains=query) | 
            Q(usuario__last_name__icontains=query) |           
            Q(profesion__icontains=query)
        ).distinct()

        # 3. Búsqueda Empresas
        empresas = Empresa.objects.filter(
            Q(nombre__icontains=query) | 
            Q(nit__icontains=query)
        )
        
        # 4. Búsqueda Usuarios (General) - NUEVO BLOQUE
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
        'total_resultados': total
    }
    
    return render(request, 'core/resultados_busqueda.html', context)
