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
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
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
    # Campos del modelo User (Nombre, Apellido, Email)
    first_name = forms.CharField(label='Nombres', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Apellidos', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Correo', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    # Campo del modelo Perfil (Foto) - ¡Lo agregamos aquí mismo para facilitar todo!
    foto_perfil = forms.ImageField(label='Foto de Perfil', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    # Campo Teléfono (Opcional, si quieres que lo editen aquí)
    telefono = forms.CharField(label='Teléfono', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        # Necesitamos recibir la instancia del perfil para cargar la foto/telefono actual
        self.perfil_instance = kwargs.pop('perfil_instance', None)
        super(MiPerfilForm, self).__init__(*args, **kwargs)
        
        # Si el perfil existe, cargamos los valores iniciales
        if self.perfil_instance:
            self.fields['foto_perfil'].initial = self.perfil_instance.foto_perfil
            self.fields['telefono'].initial = self.perfil_instance.telefono

    def save(self, commit=True):
        # Guardamos el usuario (User)
        user = super(MiPerfilForm, self).save(commit=commit)
        
        # Guardamos manualmente los datos extra en el Perfil
        if self.perfil_instance:
            self.perfil_instance.foto_perfil = self.cleaned_data['foto_perfil']
            self.perfil_instance.telefono = self.cleaned_data['telefono']
            if commit:
                self.perfil_instance.save()
        return user


# ===================================================================
# FORMULARIO PARA SINCRONIZACIÓN DE PERFIL DEL APRENDIZ COMPLETO
# ===================================================================
class AprendizPerfilForm(forms.ModelForm):
    # 1. Campos del modelo User
    first_name = forms.CharField(max_length=150, required=True, label="Nombres *", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos *", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, label="Correo Institucional *", widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Aprendiz
        # Aquí ponemos TODOS los campos que tienes en tu formulario de creación
        # (OJO: Asegúrate de que estos nombres coincidan con los de tu models.py)
        fields = [
            'tipo_documento', 
            'documento', 
            'telefono', 
            'correo_personal', 
            'direccion_residencia', 
            'numero_ficha',
            'modalidad_formacion', 
            'modalidad_etapa', 
            'etapa_exterior', 
            'pais_etapa'
        ]
        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # El documento no debería poder cambiarlo él mismo
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'ficha': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_etapa': forms.Select(attrs={'class': 'form-select'}),
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

    def save(self, commit=True):
        aprendiz = super(AprendizPerfilForm, self).save(commit=False)
        user = aprendiz.usuario
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            aprendiz.save()
            
        return aprendiz