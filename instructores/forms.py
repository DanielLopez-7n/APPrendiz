from django import forms
from .models import Instructor

class InstructorForm(forms.ModelForm):
    def clean_cedula(self):
        cedula = (self.cleaned_data.get('cedula') or '').strip()
        if not cedula.isdigit():
            raise forms.ValidationError('La cédula solo permite números (sin letras ni símbolos).')
        if len(cedula) < 6 or len(cedula) > 20:
            raise forms.ValidationError('La cédula debe tener entre 6 y 20 dígitos.')
        return cedula

    def clean_telefono(self):
        telefono = (self.cleaned_data.get('telefono') or '').strip()
        if telefono and (not telefono.isdigit() or len(telefono) < 7 or len(telefono) > 15):
            raise forms.ValidationError('El teléfono debe tener entre 7 y 15 dígitos numéricos.')
        return telefono

    class Meta:
        model = Instructor
        exclude = ['usuario']
        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 1002345678',
                'inputmode': 'numeric',
                'pattern': '[0-9]*'
            }),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3001234567'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle 123 # 45-67'}),
            
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Ing. Eléctrico'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
        }
