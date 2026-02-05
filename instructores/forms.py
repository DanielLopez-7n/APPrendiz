from django import forms
from .models import Instructor
# Importamos el formulario de usuario genérico (sin contraseña)
from usuarios.forms import UsuarioForm 

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['profesion', 'cedula', 'telefono', 'tipo_contrato']
        
        widgets = {
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ing. de Sistemas'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
        }
        1