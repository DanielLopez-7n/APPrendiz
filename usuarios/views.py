from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from .forms import LoginForm, RegistroForm, EditarUsuarioForm, EditarPerfilForm, MiPerfilForm, UsuarioForm
from aprendices.forms import AprendizForm
from instructores.forms import InstructorForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# ==================== VISTAS DE AUTENTICACIÓN ====================

@csrf_protect
@never_cache
def login_view(request):
    """
    Vista para el inicio de sesión desde el Modal del Index
    """
    # Si ya está logueado, no tiene nada que hacer aquí
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('core:dashboard')
        else:
            return redirect('aprendices:perfil_aprendiz')
    
    if request.method == 'POST':
        # .strip() elimina espacios en blanco accidentales que el usuario haya copiado
        username_input = request.POST.get('username', '').strip()
        
        # =========================================================
        # VALIDACIÓN INFALIBLE: Interceptar usuarios inactivos
        # =========================================================
        if username_input:
            User = get_user_model()
            
            # Buscamos de forma segura sin que la app se caiga si no existe
            user_check = User.objects.filter(
                Q(username=username_input) | 
                Q(documento=username_input) | 
                Q(email=username_input)
            ).first()

            # Si el usuario existe y su estado es inactivo
            if user_check and not user_check.is_active:
                # Lanzamos la alerta roja
                messages.error(request, 'Tu cuenta ha sido deshabilitada por un administrador. Si crees que es un error, por favor comunícate con soporte.')
                # Y lo regresamos al index (donde verá la alerta inmediatamente)
                return redirect('core:index') 
        # =========================================================

        # Si el usuario está activo (o no existe), el formulario nativo hace su magia
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me')
            
            if user is not None:
                login(request, user)
                
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
                
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                elif user.is_staff:
                    return redirect('core:dashboard')
                else:
                    return redirect('aprendices:perfil_aprendiz')
        else:
            # Si el formulario no es válido, es porque la contraseña está mal o el usuario no existe
            messages.error(request, 'Documento o contraseña incorrectos.')
            return redirect('core:index')

    # Si intentan entrar a /usuarios/login/ tipeando la URL, los devolvemos al inicio
    return redirect('core:index')


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


# ==================== LÓGICA DE CONTROL DE ACCESO (RBAC) ====================

def es_administrador(user):
    """
    Verifica si el usuario tiene privilegios de administrador global.
    Retorna True solo si es superusuario o si es staff pero NO tiene perfil de instructor.
    """
    if user.is_superuser:
        return True
    if user.is_staff and not hasattr(user, 'instructor'):
        return True
    return False


@login_required
@user_passes_test(es_administrador, login_url='usuarios:login')
@never_cache
def lista_usuarios_view(request):
    """
    Vista para listar todos los usuarios
    """
    # Obtener parámetros de búsqueda y filtrado
    busqueda = request.GET.get('buscar', '')
    filtro_activo = request.GET.get('activo', '')
    filtro_rol = request.GET.get('rol', '')
    
    # Query base
    usuarios = User.objects.select_related('perfil', 'aprendiz', 'instructor').all()
    
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
    
    if filtro_rol == 'administrador':
        usuarios = usuarios.filter(is_staff=True).exclude(instructor__isnull=False)
    elif filtro_rol == 'instructor':
        usuarios = usuarios.filter(instructor__isnull=False)
    elif filtro_rol == 'aprendiz':
        usuarios = usuarios.filter(aprendiz__isnull=False)
    
    # Ordenar
    usuarios = usuarios.order_by('-date_joined')

    for usuario in usuarios:
        telefono_contacto = usuario.perfil.telefono if hasattr(usuario, 'perfil') else ''
        if hasattr(usuario, 'aprendiz') and usuario.aprendiz.telefono:
            telefono_contacto = usuario.aprendiz.telefono
        elif hasattr(usuario, 'instructor') and usuario.instructor.telefono:
            telefono_contacto = usuario.instructor.telefono
        usuario.telefono_contacto = telefono_contacto
    
    context = {
        'titulo': 'Gestión de Usuarios',
        'usuarios': usuarios,
        'busqueda': busqueda,
        'filtro_activo': filtro_activo,
        'filtro_rol': filtro_rol,
    }
    return render(request, 'usuarios/listar_usuarios.html', context)


# ---ver detalle usuario ---
@login_required
@user_passes_test(es_administrador, login_url='usuarios:login')
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


@login_required
def crear_usuario_con_perfil(request):
    es_instructor = hasattr(request.user, 'instructor')
    es_admin = request.user.is_superuser or (request.user.is_staff and not es_instructor)

    if request.method == 'POST':
        # OJO AQUÍ: Asegúrate de que tu HTML tenga <select name="rol_seleccionado">
        rol = request.POST.get('rol_seleccionado')
        print(f"🕵️‍♂️ ROL DETECTADO AL GUARDAR: '{rol}'") # Chismoso 1

        form_usuario = UsuarioForm(request.POST)
        
        if rol == 'aprendiz':
            form_perfil_aprendiz = AprendizForm(request.POST)
            form_perfil_instructor = InstructorForm() 
            form_perfil = form_perfil_aprendiz
        else:
            form_perfil_instructor = InstructorForm(request.POST)
            form_perfil_aprendiz = AprendizForm() 
            form_perfil = form_perfil_instructor

        if form_usuario.is_valid() and form_perfil.is_valid():
            # 1. Crear el Usuario base
            usuario = form_usuario.save(commit=False)
            documento = form_usuario.cleaned_data['username']
            usuario.set_password(documento)
            
            if rol == 'instructor':
                usuario.is_staff = True
            
            usuario.save()

            # 2. Crear el Perfil
            perfil = form_perfil.save(commit=False)
            perfil.usuario = usuario
            if rol == 'aprendiz':
                perfil.documento = documento
            else:
                perfil.cedula = documento
            perfil.save()

            messages.success(request, f'¡Registro exitoso! Se creó el usuario y el perfil de {rol}.')
            return redirect('usuarios:lista_usuarios')
            
        else:
            # AQUÍ ES DONDE VAN LOS PRINTS (Cuando falla la validación)
            print("❌ LA VALIDACIÓN FALLÓ, REVISANDO ERRORES...")
            print("❌ Errores del Usuario:", form_usuario.errors)
            print("❌ Errores del Perfil:", form_perfil.errors)
            messages.error(request, "Hay errores en el formulario, revisa los datos.")
            
    else:
        # Petición GET: Carga inicial de la página (¡NO BORRAR ESTO!)
        form_usuario = UsuarioForm()
        form_perfil_aprendiz = AprendizForm()
        form_perfil_instructor = InstructorForm()

    context = {
        'form_usuario': form_usuario,
        'form_aprendiz': form_perfil_aprendiz,
        'form_instructor': form_perfil_instructor,
        'es_admin': es_admin,
        'es_instructor': es_instructor,
    }
    return render(request, 'usuarios/crear_usuario_dinamico.html', context)


# --- VISTA PARA VER PERFIL PROPIO (READ) ---

@login_required
@user_passes_test(es_administrador, login_url='usuarios:login')
def editar_usuario_view(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        form_perfil = EditarPerfilForm(request.POST, request.FILES, instance=usuario.perfil)
        
        # 1. PRIMERO VALIDAMOS (Esto genera el 'cleaned_data')
        if form_usuario.is_valid() and form_perfil.is_valid():
            
            # 🛡️ --- INICIO DEL BLINDAJE --- 🛡️
            # Verificamos si es el mismo usuario y si intentó ponerse "inactivo" (False)
            if usuario.id == request.user.id and form_usuario.cleaned_data.get('is_active') is False:
                messages.error(request, '¡Alerta de seguridad! No puedes desactivar tu propia cuenta mientras estás usándola.')
                return redirect('usuarios:editar_usuario', user_id=usuario.id)
            # 🛡️ --- FIN DEL BLINDAJE --- 🛡️
            
            # 2. SI PASA EL BLINDAJE, GUARDAMOS
            form_usuario.save()
            form_perfil.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado exitosamente.')
            
            return redirect('usuarios:lista_usuarios') 
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    
    else:
        form_usuario = EditarUsuarioForm(instance=usuario)
        
        documento_real = ''
        telefono_real = ''
        
        if hasattr(usuario, 'aprendiz'):
            documento_real = usuario.aprendiz.documento
            telefono_real = usuario.aprendiz.telefono
        elif hasattr(usuario, 'instructor'):
            documento_real = usuario.instructor.cedula
            telefono_real = usuario.instructor.telefono
        else:
            documento_real = usuario.perfil.documento
            telefono_real = usuario.perfil.telefono

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



# --- VISTA PARA ELIMINAR USUARIOS (DELETE) ---

@login_required
@user_passes_test(es_administrador, login_url='usuarios:login')
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


# ==================== VISTAS DE PERFIL Y CONFIGURACIÓN PERSONAL ====================

@login_required
def perfil_view(request):
    """
    Vista para que el usuario vea/edite su propio perfil.
    Carga dinámicamente el panel correcto y desbloquea campos para los instructores/admins.
    """
    usuario = request.user
    template_base = 'core/panel_admin_base.html' if usuario.is_staff else 'core/base_simple.html'
    cancel_url = 'core:dashboard' if usuario.is_staff else 'aprendices:perfil_aprendiz'
    
    if request.method == 'POST':
        form_usuario = EditarUsuarioForm(request.POST, instance=usuario)
        
        # Le pasamos el 'usuario=usuario' para que el formulario sepa si desbloquear los campos
        form_perfil = EditarPerfilForm(request.POST, request.FILES, instance=usuario.perfil, usuario=usuario)
        
        if form_usuario.is_valid() and form_perfil.is_valid():
            # 1. Guardamos datos del Usuario (Nombre, Apellido, Correo)
            usuario_seguro = form_usuario.save(commit=False)
            usuario_seguro.save(update_fields=['first_name', 'last_name', 'email'])
            
            # 2. Guardamos datos del Perfil (Foto, Teléfono, Documento)
            perfil_guardado = form_perfil.save()
            
            # 3. SINCRONIZACIÓN (Premium): Si es Instructor, guardamos el teléfono también en su tabla
            if hasattr(usuario, 'instructor'):
                usuario.instructor.telefono = perfil_guardado.telefono
                # Si tu modelo Instructor también tiene documento, descomenta la siguiente línea:
                # usuario.instructor.documento = perfil_guardado.documento
                usuario.instructor.save()
            
            messages.success(request, 'Tu información personal se ha actualizado exitosamente.')
            return redirect('usuarios:perfil') 
        else:
            messages.error(request, 'Hubo un error al actualizar tu perfil. Revisa los datos.')
    else:
        # Modo lectura (Cuando apenas abren la página)
        form_usuario = EditarUsuarioForm(instance=usuario)
        # Le pasamos el usuario también al cargar el formulario en blanco
        form_perfil = EditarPerfilForm(instance=usuario.perfil, usuario=usuario)
    
    context = {
        'titulo': 'Mi información personal',
        'usuario': usuario,
        'form_usuario': form_usuario,
        'form_perfil': form_perfil,
        'template_to_extend': template_base,
        'cancel_url': cancel_url,
        'rol_usuario': (
            'Administrador'
            if usuario.is_superuser
            else 'Instructor' if hasattr(usuario, 'instructor')
            else 'Aprendiz' if hasattr(usuario, 'aprendiz')
            else 'Usuario'
        ),
        'fecha_registro': usuario.date_joined,
        'ultimo_acceso': usuario.last_login,
    }

    # Datos extendidos para pintar una ficha completa del perfil según tipo de usuario
    documento_sistema = usuario.perfil.documento or usuario.username
    telefono_sistema = usuario.perfil.telefono or 'No registrado'
    direccion_sistema = usuario.perfil.direccion or 'No registrada'
    correo_personal = 'No registrado'
    tipo_documento = 'No definido'

    if hasattr(usuario, 'instructor'):
        instructor = usuario.instructor
        documento_sistema = instructor.cedula or documento_sistema
        telefono_sistema = instructor.telefono or telefono_sistema
        direccion_sistema = instructor.direccion_residencia or direccion_sistema
        correo_personal = instructor.correo_personal or correo_personal
        tipo_documento = instructor.get_tipo_documento_display()
        context['profesion'] = instructor.profesion
        context['tipo_contrato'] = instructor.get_tipo_contrato_display()
    elif hasattr(usuario, 'aprendiz'):
        aprendiz = usuario.aprendiz
        documento_sistema = aprendiz.documento or documento_sistema
        telefono_sistema = aprendiz.telefono or telefono_sistema
        direccion_sistema = aprendiz.direccion_residencia or direccion_sistema
        correo_personal = aprendiz.correo_personal or correo_personal
        tipo_documento = aprendiz.get_tipo_documento_display()
        context['ficha_actual'] = getattr(aprendiz.numero_ficha, 'numero', 'No asignada')
        context['programa_formacion'] = getattr(getattr(aprendiz.numero_ficha, 'programa', None), 'nombre', 'No asignado')

    context.update({
        'documento_sistema': documento_sistema,
        'telefono_sistema': telefono_sistema,
        'direccion_sistema': direccion_sistema,
        'correo_personal': correo_personal,
        'tipo_documento': tipo_documento,
    })
    return render(request, 'usuarios/perfil.html', context)

# --- VISTA DE CAMBIO DE CONTRASEÑA ---

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # Mantiene la sesión viva
            messages.success(request, '¡Excelente! Tu contraseña ha sido actualizada y tu cuenta ahora es segura.')
            
            # REDIRECCIÓN INTELIGENTE
            if user.is_staff or user.is_superuser:
                return redirect('core:dashboard') # Instructores y Admins
            else:
                return redirect('aprendices:perfil_aprendiz') # Aprendices <-- ¡AQUÍ ESTÁ LA CORRECCIÓN!
        else:
            messages.error(request, 'Hubo un error. Por favor, revisa las validaciones del formulario.')
    else:
        form = PasswordChangeForm(request.user)

    # PLANTILLA BASE DINÁMICA
    plantilla_base = 'core/panel_admin_base.html' if request.user.is_staff else 'core/base_simple.html'

    context = {
        'form': form,
        'titulo': 'Cambiar Contraseña',
        'plantilla_base': plantilla_base
    }
    return render(request, 'usuarios/cambiar_password.html', context)
