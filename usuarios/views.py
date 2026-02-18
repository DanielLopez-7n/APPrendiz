from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from .forms import LoginForm, RegistroForm, EditarUsuarioForm, EditarPerfilForm, MiPerfilForm, UsuarioForm

# ==================== VISTAS DE AUTENTICACIÓN ====================

@csrf_protect
@never_cache
def login_view(request):
    """
    Vista para el inicio de sesión de usuarios
    """
    # 1. MEJORA AL PRINCIPIO:
    # Si el usuario ya está autenticado, redirigir según su ROL
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('core:dashboard')
        else:
            return redirect('aprendices:perfil_aprendiz')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Autenticar usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Configurar duración de la sesión
                    if not remember_me:
                        request.session.set_expiry(0)  # Expira al cerrar navegador
                    
                    messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
                    
                    # Redirigir según el tipo de usuario
                    next_url = request.POST.get('next') or request.GET.get('next')
                    
                    if next_url:
                        return redirect(next_url)
                    
                    # 2. EL CAMBIO QUE PEDISTE AQUÍ 👇
                    elif user.is_staff:
                        # Si es Instructor/Admin -> Dashboard
                        return redirect('core:dashboard')
                    else:
                        # Si es Aprendiz -> Su Perfil Nuevo 🚀
                        return redirect('aprendices:perfil_aprendiz')
                        
                else:
                    messages.error(request, 'Esta cuenta ha sido desactivada.')
            else:
                messages.error(request, 'Documento o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'titulo': 'Iniciar Sesión'
    }
    return render(request, 'usuarios/login.html', context)


@csrf_protect
def registro_view(request):
    """
    Vista para el registro de nuevos usuarios
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(
                request, 
                f'Cuenta creada exitosamente para {user.get_full_name()}. '
                'Ya puedes iniciar sesión.'
            )
            return redirect('usuarios:login')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    context = {
        'form': form,
        'titulo': 'Registro de Usuario'
    }
    return render(request, 'usuarios/registro.html', context)


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:index')


# ==================== PANEL DE ADMINISTRACIÓN ====================

def es_staff(user):
    """Función auxiliar para verificar si el usuario es staff"""
    return user.is_staff



@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def lista_usuarios_view(request):
    """
    Vista para listar todos los usuarios
    """
    # Obtener parámetros de búsqueda y filtrado
    busqueda = request.GET.get('buscar', '')
    filtro_activo = request.GET.get('activo', '')
    filtro_staff = request.GET.get('staff', '')
    
    # Query base
    usuarios = User.objects.select_related('perfil').all()
    
    # Aplicar filtros
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(perfil__documento__icontains=busqueda)
        )
    
    if filtro_activo:
        usuarios = usuarios.filter(is_active=filtro_activo == 'true')
    
    if filtro_staff:
        usuarios = usuarios.filter(is_staff=filtro_staff == 'true')
    
    # Ordenar
    usuarios = usuarios.order_by('-date_joined')
    
    context = {
        'titulo': 'Gestión de Usuarios',
        'usuarios': usuarios,
        'busqueda': busqueda,
        'filtro_activo': filtro_activo,
        'filtro_staff': filtro_staff,
    }
    return render(request, 'usuarios/listar_usuarios.html', context)

 # ---ver detalle usuario ---
@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def ver_detalle_usuario(request, user_id):
    """
    Vista para ver el detalle de un usuario específico
    """
    usuario = get_object_or_404(User, id=user_id)
    
    context = {
        'titulo': f'Detalle de Usuario: {usuario.get_full_name()}',
        'usuario': usuario
    }
    return render(request, 'usuarios/ver_detalle.html', context)

# --------------------------------------------------


@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def crear_usuario_view(request):
    """
    Vista para crear un nuevo usuario base (Aprendiz/Instructor)
    sin pedir contraseña (se asigna el documento por defecto).
    """
    if request.method == 'POST':
        # USAMOS EL NUEVO FORMULARIO SIMPLIFICADO
        form = UsuarioForm(request.POST) 
        
        if form.is_valid():
            # 1. Preparamos el usuario pero no lo guardamos aún
            user = form.save(commit=False)
            
            # 2. La contraseña será el mismo número de documento (username)
            documento = form.cleaned_data['username']
            user.set_password(documento)
            
            # 3. Guardamos el User. ¡Magia! Esto dispara tu señal en models.py
            # y crea el PerfilUsuario automáticamente en el fondo.
            user.save()
            
            # 4. Ahora tomamos ese perfil recién creado y le asignamos el documento real
            user.perfil.documento = documento
            user.perfil.save()
            
            messages.success(request, f'¡Cuenta de acceso creada! La contraseña temporal es el documento: {documento}. Ahora puedes ir a vincularla en Aprendices o Instructores.')
            return redirect('usuarios:lista_usuarios')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UsuarioForm()
    
    context = {
        'titulo': 'Crear Cuenta de Acceso (Base)',
        'form': form,
        'accion': 'Crear'
    }
    
    return render(request, 'usuarios/crear_usuario.html', context)
# usuarios/views.py

@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def editar_usuario_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        form_perfil = EditarPerfilForm(request.POST, request.FILES, instance=usuario.perfil)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado exitosamente.')
            
            # CORRECCIÓN DEL REDIRECT (sin la 'r' extra)
            return redirect('usuarios:lista_usuarios') 
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    
    else:
        # --- LÓGICA GET (MOSTRAR DATOS) ---
        form_usuario = EditarUsuarioForm(instance=usuario)
        
        # 1. Variables para guardar los datos reales
        documento_real = ''
        telefono_real = ''
        
        # 2. Buscamos en Aprendiz
        if hasattr(usuario, 'aprendiz'):
            documento_real = usuario.aprendiz.documento
            telefono_real = usuario.aprendiz.telefono
            
        # 3. Buscamos en Instructor
        elif hasattr(usuario, 'instructor'):
            documento_real = usuario.instructor.cedula
            telefono_real = usuario.instructor.telefono
            
        # 4. Si es Admin o Staff (usamos los del perfil base)
        else:
            documento_real = usuario.perfil.documento
            telefono_real = usuario.perfil.telefono

        # 5. Inyectamos AMBOS datos en el formulario visual
        form_perfil = EditarPerfilForm(
            instance=usuario.perfil, 
            initial={
                'documento': documento_real,
                'telefono': telefono_real
            }
        )

    context = {
        'titulo': f'Editar Usuario: {usuario.get_full_name()}',
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'usuario': usuario,
        'accion': 'Actualizar'
    }
    return render(request, 'usuarios/editar_usuario.html', context)

@login_required
@user_passes_test(es_staff, login_url='usuarios:login')
def eliminar_usuario_view(request, user_id):
    """
    Vista para eliminar DEFINITIVAMENTE un usuario de la base de datos
    """
    usuario = get_object_or_404(User, id=user_id)
    
    # No permitir eliminar al superusuario
    if usuario.is_superuser:
        messages.error(request, 'No se puede eliminar un administrador principal.')
        return redirect('usuarios:lista_usuarios')
    
    # No permitir que se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta en uso.')
        return redirect('usuarios:lista_usuarios')
    
    if request.method == 'POST':
        nombre = usuario.get_full_name() or usuario.username
        
        # ¡LA INSTRUCCIÓN DE BORRADO DEFINITIVO!
        usuario.delete() 
        
        messages.success(request, f'El usuario {nombre} fue eliminado permanentemente de la base de datos.')
        return redirect('usuarios:lista_usuarios')
    
    # Si intentan entrar por URL directa (GET), los devolvemos a la lista
    return redirect('usuarios:lista_usuarios')


@login_required
def perfil_view(request):
    """
    Vista para que el usuario vea/edite su propio perfil
    """
    usuario = request.user
    
    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        form_perfil = EditarPerfilForm(request.POST, request.FILES, instance=usuario.perfil)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            form_usuario.save()
            form_perfil.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
    else:
        form_usuario = EditarUsuarioForm(instance=usuario)
        form_perfil = EditarPerfilForm(instance=usuario.perfil)
    
    context = {
        'titulo': 'Mi Perfil',
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def editar_mi_perfil(request):
    usuario = request.user
    perfil = usuario.perfil
    
    if request.method == 'POST':
        # Pasamos POST, FILES (para la foto) y la instancia del perfil
        form = MiPerfilForm(request.POST, request.FILES, instance=usuario, perfil_instance=perfil)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado!')
            return redirect('usuarios:ver_perfil') # Redirige a la vista de "Ver Perfil" (solo lectura)
    else:
        form = MiPerfilForm(instance=usuario, perfil_instance=perfil)
    
    return render(request, 'usuarios/editar_mi_perfil.html', {
        'form': form
    })
    