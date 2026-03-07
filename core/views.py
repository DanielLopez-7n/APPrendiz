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
            instructor = user.instructor
            # Consultamos solo las bitácoras asignadas a ÉL
            pendientes = Bitacora.objects.filter(instructor_seguimiento=instructor, estado='Pendiente').count()
            evaluadas = Bitacora.objects.filter(instructor_seguimiento=instructor, estado='Evaluada').count()
            rechazadas = Bitacora.objects.filter(instructor_seguimiento=instructor, estado='Rechazada').count()
            
            context.update({
                'pendientes': pendientes,
                'evaluadas': evaluadas,
                'total_bitacoras': pendientes + evaluadas + rechazadas,
            })
            
            # Datos para Gráfica de Instructor (Estado de sus Bitácoras)
            context['chart_labels'] = json.dumps(['Pendientes', 'Evaluadas', 'Rechazadas'])
            context['chart_data'] = json.dumps([pendientes, evaluadas, rechazadas])
            
        except Exception:
            # En caso de que el instructor no tenga datos aún
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