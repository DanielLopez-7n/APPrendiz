from django import forms
from django.contrib.auth.models import User
from .models import Instructor

# 1. Formulario para la cuenta de usuario (Login)
class UsuarioInstructorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula o usuario'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Institucional',
            'username': 'Usuario',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

# 2. Formulario para los datos específicos del Instructor
class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['profesion', 'telefono']
        widgets = {
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ingeniero de Sistemas'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'profesion': 'Profesión / Especialidad',
            'telefono': 'Celular de contacto',
        }