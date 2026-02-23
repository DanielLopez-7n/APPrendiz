from django import forms
from .models import Instructor

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        exclude = ['usuario']
        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1002345678'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3001234567'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle 123 # 45-67'}),
            
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Ing. Eléctrico'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
        }