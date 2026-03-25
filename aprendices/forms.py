from django import forms
from .models import Aprendiz

class AprendizForm(forms.ModelForm):
    def clean_documento(self):
        documento = (self.cleaned_data.get('documento') or '').strip()
        if not documento.isdigit():
            raise forms.ValidationError('El documento solo permite números (sin letras ni símbolos).')
        return documento

    class Meta:
        model = Aprendiz
        exclude = ['usuario', 'programa_formacion']        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 1002345678',
                'inputmode': 'numeric',
                'pattern': '[0-9]*'
            }),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3001234567'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle 123 # 45-67'}),
            
            'numero_ficha': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            
            'modalidad_etapa': forms.Select(attrs={'class': 'form-select'}),
            'pais_etapa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Colombia'}),
            # Al checkbox le ponemos la clase especial form-check-input
            'etapa_exterior': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }
