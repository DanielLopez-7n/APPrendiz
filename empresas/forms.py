from django import forms
from .models import Empresa

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'nit', 'direccion', 'telefono', 
                 'nombre_jefe', 'cargo_jefe', 'telefono_jefe', 'correo_jefe']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tech Solutions S.A.S'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 900.123.456-1'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_jefe': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Razón Social de la Empresa',
            'nombre_jefe': 'Nombre del Coformador (Jefe)',
        }