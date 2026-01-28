from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

# Importamos los modelos de nuestras Apps para las estadísticas
from aprendices.models import Aprendiz
from empresas.models import Empresa
from bitacoras.models import Bitacora

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
    # 1. Estadísticas de APPRENDIZ (Lo que necesita el HTML nuevo)
    total_aprendices = Aprendiz.objects.count()
    total_empresas = Empresa.objects.count()
    
    # Contamos bitácoras que NO han sido evaluadas por instructor
    bitacoras_pendientes = Bitacora.objects.filter(evaluado_instructor=False).count()
    
    # Traemos las últimas 5 para la tabla de resumen
    ultimas_bitacoras = Bitacora.objects.all().order_by('-fecha_creacion')[:5]

    # 2. Estadísticas de Usuarios (Lo que tenías antes, por si lo quieres usar)
    total_usuarios = User.objects.count()
    usuarios_activos = User.objects.filter(is_active=True).count()

    context = {
        'titulo': 'Panel de Control',
        # Datos para las Tarjetas (Cards)
        'total_aprendices': total_aprendices,
        'total_empresas': total_empresas,
        'bitacoras_pendientes': bitacoras_pendientes,
        'ultimas_bitacoras': ultimas_bitacoras,
        # Datos extra de sistema
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