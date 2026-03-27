from django import forms
from .models import Programa
from core.form_validators import validate_digits, validate_text_length


class ProgramaForm(forms.ModelForm):
    class Meta:
        model = Programa
        fields = ['nombre', 'codigo', 'nivel']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Análisis y Desarrollo de Software'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2560321'
            }),
            'nivel': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nombre': 'Nombre del Programa de Formación',
            'codigo': 'Código Programa',
            'nivel': 'Nivel de Formación',
        }

    def clean_nombre(self):
        nombre = validate_text_length(self.cleaned_data.get('nombre'), 'nombre del programa', min_len=5, max_len=120)
        if nombre.isdigit():
            raise forms.ValidationError('El nombre del programa no puede contener solo números.')
        return nombre

    def clean_codigo(self):
        return validate_digits(self.cleaned_data.get('codigo'), 'código del programa', min_len=3, max_len=20)
