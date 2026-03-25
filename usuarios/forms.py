from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario
from aprendices.models import Aprendiz

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para inicio de sesión
    Usamos el campo username para almacenar el documento
    """
    username = forms.CharField(
        label='Documento',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su documento',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Recordarme'
    )


class RegistroForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios
    Extiende UserCreationForm de Django
    """
    documento = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control d-none'}),  # Oculto, usamos documento
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        }
    
    def clean_documento(self):
        """Valida que el documento no exista en la base de datos"""
        documento = self.cleaned_data.get('documento')
        if PerfilUsuario.objects.filter(documento=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado.')
        return documento
    
    def clean_email(self):
        """Valida que el email no exista en la base de datos"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        """
        Guarda el usuario y crea su perfil con el documento
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data['documento']  # Usamos documento como username
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # El perfil se crea automáticamente por la señal
            perfil = user.perfil
            perfil.documento = self.cleaned_data['documento']
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.save()
        
        return user


class EditarUsuarioForm(forms.ModelForm):
    """
    Formulario para editar información del usuario
    """
    # usuarios/forms.py

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        # 1. AQUÍ: Agrega el campo is_active para activar/desactivar usuario
        fields = ['first_name', 'last_name', 'email', 'is_active']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            
            # 2. AQUÍ: Define el estilo para que se vea como switch
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
            'is_staff': 'Acceso al Panel Admin',
        }


class EditarPerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil del usuario
    """
    class Meta:
        model = PerfilUsuario
        fields = ['documento', 'telefono', 'direccion', 'foto_perfil', 'fecha_nacimiento']        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}), # Añadido para el username
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
    # Sacamos al usuario de los argumentos
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        # Si el usuario es Admin o Instructor, DESBLOQUEAMOS los campos
        if self.usuario and self.usuario.is_staff:
            if 'documento' in self.fields:
                self.fields['documento'].widget.attrs.pop('readonly', None)
                self.fields['documento'].widget.attrs['class'] = 'form-control'
                self.fields['documento'].label = "Documento de Identidad"
                
            if 'telefono' in self.fields:
                self.fields['telefono'].widget.attrs.pop('readonly', None)
                self.fields['telefono'].widget.attrs['class'] = 'form-control'
                self.fields['telefono'].label = "Teléfono de Contacto"
        
# --- Nuevo formulario agregado para usuarios sin contraseña ---

class UsuarioForm(forms.ModelForm):
    """
    Formulario simplificado para crear usuarios (Aprendices/Instructores)
    SIN pedir contraseña (se genera automática).
    """
    class Meta:
        model = User
        # Solo pedimos estos 4 datos
        fields = ['first_name', 'last_name', 'email', 'username']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@misena.edu.co'}),
            # Al username le ponemos placeholder más descriptivo
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento, nombre...'}),
        }
        
        labels = {
            'username': 'Número de Documento (Usuario)',
            'email': 'Correo Institucional',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
        }

    def clean_email(self):
        """Validar que el correo no se repita"""
        email = self.cleaned_data.get('email')
        # Si estamos editando (self.instance.pk existe), excluimos al usuario actual de la búsqueda
        if self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este correo ya está registrado por otro usuario.')
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_username(self):
        """Validar que el documento no se repita"""
        username = self.cleaned_data.get('username')
        if self.instance.pk:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este documento ya está registrado.')
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Este documento ya está registrado.')
        return username
    
    # Nuevo formulario para que los usuarios editen su propio perfil

class MiPerfilForm(forms.ModelForm):
    # Solo definimos los campos que NO pertenecen al modelo User (sino al Perfil)
    foto_perfil = forms.ImageField(label='Foto de Perfil', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(label='Teléfono', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        # 🛡️ Blindaje: Solo estos campos del User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.perfil_instance = kwargs.pop('perfil_instance', None)
        super(MiPerfilForm, self).__init__(*args, **kwargs)
        
        # Cargamos el teléfono actual si existe
        if self.perfil_instance:
            self.fields['telefono'].initial = self.perfil_instance.telefono

    def save(self, commit=True):
        # Guardamos la instancia base del usuario sin enviarla a la base de datos aún
        user = super(MiPerfilForm, self).save(commit=False)
        
        if commit:
            # 1. Guardamos SOLAMENTE los campos permitidos del usuario (Nombres y Correo)
            user.save(update_fields=['first_name', 'last_name', 'email'])
            
            # 2. Guardamos los datos del Perfil adicional (Teléfono y Foto)
            if self.perfil_instance:
                self.perfil_instance.telefono = self.cleaned_data.get('telefono')
                
                # 'changed_data' detecta si el usuario realmente subió un archivo nuevo
                if 'foto_perfil' in self.changed_data:
                    self.perfil_instance.foto_perfil = self.cleaned_data.get('foto_perfil')
                    
                self.perfil_instance.save()
                
        return user

# ===================================================================
# FORMULARIO PARA SINCRONIZACIÓN DE PERFIL DEL APRENDIZ COMPLETO
# ===================================================================
class AprendizPerfilForm(forms.ModelForm):
    # 1. Campos del modelo User (Sesión segura)
    first_name = forms.CharField(max_length=150, required=True, label="Nombres *", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos *", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label="Correo Institucional *", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    # 2. CAMPO PARA LA FOTO
    foto_perfil = forms.ImageField(required=False, label="Foto de Perfil", widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Aprendiz
        fields = [
            'tipo_documento', 'documento', 'telefono', 'correo_personal', 
            'direccion_residencia', 'numero_ficha', 'modalidad_formacion', 
            'modalidad_etapa', 'empresa', 'etapa_exterior', 'pais_etapa'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'ficha': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_etapa': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'etapa_exterior': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pais_etapa': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AprendizPerfilForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            # Cargamos la foto actual si existe en su perfil
            if hasattr(user, 'perfil') and user.perfil.foto_perfil:
                self.fields['foto_perfil'].initial = user.perfil.foto_perfil

    def save(self, commit=True):
        aprendiz = super(AprendizPerfilForm, self).save(commit=False)
        user = aprendiz.usuario
        
        # Actualizamos SOLO los datos de texto (NUNCA el username ni el password)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            aprendiz.save()
            
            # Si subió una foto nueva, la guardamos en su perfil
            if hasattr(user, 'perfil') and 'foto_perfil' in self.cleaned_data:
                foto = self.cleaned_data['foto_perfil']
                if foto:
                    user.perfil.foto_perfil = foto
                    user.perfil.save()
            
        return aprendiz
    
    from django.contrib.auth.models import User

class EditarMiPropioUsuarioForm(forms.ModelForm):
    """
    Formulario súper seguro: Solo permite cambiar datos básicos.
    Ignora por completo el is_active, is_staff, etc.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # ¡Cero rastro de is_active!
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }