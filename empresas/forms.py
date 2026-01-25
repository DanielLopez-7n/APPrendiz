from django import forms
from .models import Empresa

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nit', 'nombre', 'direccion', 'telefono', 'encargado', 'email_encargado']
        
        widgets = {
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 900.123.456-7'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa S.A.S'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección física'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'encargado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del jefe inmediato'}),
            'email_encargado': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@empresa.com'}),
        }
        
        labels = {
            'nit': 'NIT de la Empresa',
            'nombre': 'Razón Social',
            'encargado': 'Nombre del Jefe Inmediato',
            'email_encargado': 'Correo Electrónico (Jefe)',
        }