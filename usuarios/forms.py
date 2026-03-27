from django import forms
import re
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario
from aprendices.models import Aprendiz
from instructores.models import Instructor
from aprendices.forms import PAIS_CHOICES
from core.form_validators import (
    validate_digits,
    validate_email_length,
    validate_person_name,
    validate_phone,
    validate_text_length,
)


def validar_solo_numeros(valor, etiqueta='documento'):
    return validate_digits(valor, etiqueta, min_len=1, max_len=20)


def validar_longitud_campo(valor, etiqueta, minimo=1, maximo=20):
    return validate_text_length(valor, etiqueta, min_len=minimo, max_len=maximo)


def validar_usuario_alfanumerico(valor, etiqueta='nombre de usuario', minimo=4, maximo=20):
    valor = validate_text_length(valor, etiqueta, min_len=minimo, max_len=maximo)
    if not re.fullmatch(r'[A-Za-z0-9]+', valor or ''):
        raise forms.ValidationError(
            'El nombre de usuario solo puede contener letras y números (sin espacios ni signos).'
        )
    return valor

class LoginForm(AuthenticationForm):
    """
    Formulario personalizado para inicio de sesión
    Usamos el campo username para almacenar el documento
    """
    username = forms.CharField(
        label='Usuario',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario',
            'autofocus': True,
            'autocomplete': 'username',
            'inputmode': 'text',
            'pattern': '[A-Za-z0-9]+'
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

    def clean_username(self):
        return validar_usuario_alfanumerico(self.cleaned_data.get('username'), 'usuario', minimo=4, maximo=20)


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
            'placeholder': 'Número de documento',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
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
        documento = validar_solo_numeros(self.cleaned_data.get('documento'), 'documento')
        documento = validar_longitud_campo(documento, 'documento', minimo=6, maximo=20)
        if PerfilUsuario.objects.filter(documento=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado.')
        return documento

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['maxlength'] = 70
        self.fields['last_name'].widget.attrs['maxlength'] = 70
        self.fields['email'].widget.attrs['maxlength'] = 70
    
    def clean_email(self):
        """Valida que el email no exista en la base de datos"""
        email = validate_email_length(self.cleaned_data.get('email'), max_len=70)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_first_name(self):
        return validate_person_name(self.cleaned_data.get('first_name'), 'nombre', min_len=2, max_len=70)

    def clean_last_name(self):
        return validate_person_name(self.cleaned_data.get('last_name'), 'apellido', min_len=2, max_len=70)
    
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
    def clean_first_name(self):
        return validate_person_name(self.cleaned_data.get('first_name'), 'nombre', min_len=2, max_len=70)

    def clean_last_name(self):
        return validate_person_name(self.cleaned_data.get('last_name'), 'apellido', min_len=2, max_len=70)

    def clean_email(self):
        return validate_email_length(self.cleaned_data.get('email'), max_len=70)

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
    TIPO_DOC_CHOICES = [
        ('', 'No definido'),
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PEP', 'PEP'),
        ('PAS', 'Pasaporte'),
    ]
    tipo_documento = forms.ChoiceField(
        choices=TIPO_DOC_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    class Meta:
        model = PerfilUsuario
        fields = ['tipo_documento', 'documento', 'telefono', 'direccion', 'foto_perfil', 'fecha_nacimiento']        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}), # Añadido para el username
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
    # Sacamos al usuario de los argumentos
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        # Etiquetas amigables para todos los perfiles
        self.fields['tipo_documento'].label = "Tipo de Documento"

        if self.usuario:
            tipo_doc_actual = (self.instance.tipo_documento if self.instance else '') or ''
            if hasattr(self.usuario, 'instructor'):
                tipo_doc_actual = self.usuario.instructor.tipo_documento or tipo_doc_actual
            elif hasattr(self.usuario, 'aprendiz'):
                tipo_doc_actual = self.usuario.aprendiz.tipo_documento or tipo_doc_actual
            self.fields['tipo_documento'].initial = tipo_doc_actual

            if self.instance and self.instance.fecha_nacimiento:
                self.fields['fecha_nacimiento'].initial = self.instance.fecha_nacimiento

        if 'documento' in self.fields:
            self.fields['documento'].label = "Documento de Identidad"
        if 'telefono' in self.fields:
            self.fields['telefono'].label = "Teléfono de Contacto"
        if 'direccion' in self.fields:
            self.fields['direccion'].label = "Dirección de Residencia"
        if 'fecha_nacimiento' in self.fields:
            self.fields['fecha_nacimiento'].label = "Fecha de Nacimiento"

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if not documento and self.instance:
            return self.instance.documento

        documento = validate_digits(documento, 'documento', min_len=6, max_len=20)

        perfil_qs = PerfilUsuario.objects.filter(documento=documento)
        if self.instance and self.instance.pk:
            perfil_qs = perfil_qs.exclude(pk=self.instance.pk)
        if perfil_qs.exists():
            raise forms.ValidationError('Este número de documento ya está registrado por otro usuario del sistema.')

        usuario_id_actual = getattr(self.usuario, 'id', None)
        if Aprendiz.objects.filter(documento=documento).exclude(usuario_id=usuario_id_actual).exists():
            raise forms.ValidationError('Este número de documento ya existe en un registro de aprendiz.')

        if Instructor.objects.filter(cedula=documento).exclude(usuario_id=usuario_id_actual).exists():
            raise forms.ValidationError('Este número de documento ya existe en un registro de instructor.')

        if User.objects.filter(username=documento).exclude(pk=usuario_id_actual).exists():
            raise forms.ValidationError('Este número de documento ya está en uso como usuario de acceso.')

        return documento

    def clean_telefono(self):
        return validate_phone(self.cleaned_data.get('telefono'), 'teléfono', min_len=7, max_len=15, required=False)

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if not direccion:
            return direccion
        return validate_text_length(direccion, 'dirección', min_len=5, max_len=70)

    def save(self, commit=True):
        perfil = super().save(commit=False)
        perfil.tipo_documento = self.cleaned_data.get('tipo_documento') or ''
        if commit:
            perfil.save()
        return perfil
        
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
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. user123',
                'inputmode': 'text',
                'pattern': '[A-Za-z0-9]+'
            }),
        }
        
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Institucional',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['maxlength'] = 70
        self.fields['last_name'].widget.attrs['maxlength'] = 70
        self.fields['email'].widget.attrs['maxlength'] = 70

    def clean_email(self):
        """Validar que el correo no se repita"""
        email = validate_email_length(self.cleaned_data.get('email'), max_len=70)
        # Si estamos editando (self.instance.pk existe), excluimos al usuario actual de la búsqueda
        if self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este correo ya está registrado por otro usuario.')
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_username(self):
        """Validar username alfanumérico único"""
        username = validar_usuario_alfanumerico(self.cleaned_data.get('username'), 'nombre de usuario', minimo=4, maximo=20)
        if self.instance.pk:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este nombre de usuario ya está registrado.')
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Este nombre de usuario ya está registrado.')
        return username

    def clean_first_name(self):
        return validate_person_name(self.cleaned_data.get('first_name'), 'nombre', min_len=2, max_len=70)

    def clean_last_name(self):
        return validate_person_name(self.cleaned_data.get('last_name'), 'apellido', min_len=2, max_len=70)
    
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
    etapa_exterior = forms.TypedChoiceField(
        choices=((False, 'No'), (True, 'Sí')),
        coerce=lambda x: str(x).lower() == 'true',
        empty_value=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='¿Realiza etapa en el exterior?'
    )
    pais_etapa = forms.ChoiceField(
        choices=PAIS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='País donde realiza la etapa',
        required=False,
    )

    class Meta:
        model = Aprendiz
        fields = [
            'tipo_documento', 'documento', 'telefono', 'correo_personal',
            'departamento', 'ciudad_municipio',
            'direccion_residencia', 'numero_ficha', 'modalidad_formacion', 
            'modalidad_etapa', 'etapa_exterior', 'pais_etapa'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'ciudad_municipio': forms.Select(attrs={'class': 'form-select'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control'}),
            'ficha': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_etapa': forms.Select(attrs={'class': 'form-select'}),
            'etapa_exterior': forms.Select(attrs={'class': 'form-select'}),
            'pais_etapa': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AprendizPerfilForm, self).__init__(*args, **kwargs)
        self.fields['departamento'].choices = [('', 'Seleccione un departamento...')]
        self.fields['ciudad_municipio'].choices = [('', 'Seleccione primero un departamento...')]
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            # Cargamos la foto actual si existe en su perfil
            if hasattr(user, 'perfil') and user.perfil.foto_perfil:
                self.fields['foto_perfil'].initial = user.perfil.foto_perfil

    def clean_first_name(self):
        return validate_person_name(self.cleaned_data.get('first_name'), 'nombre', min_len=2, max_len=70)

    def clean_last_name(self):
        return validate_person_name(self.cleaned_data.get('last_name'), 'apellido', min_len=2, max_len=70)

    def clean_email(self):
        return validate_email_length(self.cleaned_data.get('email'), max_len=70)

    def clean_telefono(self):
        return validate_phone(self.cleaned_data.get('telefono'), 'teléfono', min_len=7, max_len=15, required=False)

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

    def clean_documento(self):
        documento = validar_solo_numeros(self.cleaned_data.get('documento'), 'documento')
        return validar_longitud_campo(documento, 'documento', minimo=6, maximo=20)

    def clean_departamento(self):
        departamento = (self.cleaned_data.get('departamento') or '').strip()
        if len(departamento) > 70:
            raise forms.ValidationError('El departamento no puede superar 70 caracteres.')
        return departamento

    def clean_ciudad_municipio(self):
        ciudad = (self.cleaned_data.get('ciudad_municipio') or '').strip()
        if len(ciudad) > 70:
            raise forms.ValidationError('La ciudad o municipio no puede superar 70 caracteres.')
        return ciudad

    def clean(self):
        cleaned_data = super().clean()
        etapa_exterior = cleaned_data.get('etapa_exterior')
        pais_etapa = cleaned_data.get('pais_etapa')

        if etapa_exterior and not pais_etapa:
            self.add_error('pais_etapa', 'Debes seleccionar el país donde realiza la etapa.')
        if not etapa_exterior:
            cleaned_data['pais_etapa'] = 'Colombia'
        return cleaned_data
    
    from django.contrib.auth.models import User

class EditarMiPropioUsuarioForm(forms.ModelForm):
    """
    Formulario súper seguro: Solo permite cambiar datos básicos.
    Ignora por completo el is_active, is_staff, etc.
    """
    def clean_first_name(self):
        return validate_person_name(self.cleaned_data.get('first_name'), 'nombre', min_len=2, max_len=70)

    def clean_last_name(self):
        return validate_person_name(self.cleaned_data.get('last_name'), 'apellido', min_len=2, max_len=70)

    def clean_email(self):
        return validate_email_length(self.cleaned_data.get('email'), max_len=70)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # ¡Cero rastro de is_active!
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
