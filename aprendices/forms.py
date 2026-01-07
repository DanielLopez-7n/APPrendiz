from django import forms
from django.contrib.auth.models import User
from .models import Aprendiz

# Formulario A: Datos de cuenta (Usuario y Contraseña)
class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Institucional',
            'username': 'Usuario (Cédula para login)',
        }

    # Validación extra: Que las contraseñas coincidan
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

# Formulario B: Datos del SENA (Ficha y Programa)
class AprendizForm(forms.ModelForm):
    class Meta:
        model = Aprendiz
        fields = ['numero_ficha', 'programa_formacion', 'telefono']
        widgets = {
            'numero_ficha': forms.TextInput(attrs={'class': 'form-control'}),
            'programa_formacion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }