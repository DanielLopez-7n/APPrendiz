from django import forms
from .models import Programa

class ProgramaForm(forms.ModelForm):
    class Meta:
        model = Programa
        fields = ['nombre', 'codigo', 'nivel']
        # Widgets: Aquí le aplicamos las clases de Bootstrap a los inputs
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
        # Labels: Personalizamos las etiquetas si es necesario
        labels = {
            'nombre': 'Nombre del Programa de Formación',
            'codigo': 'Código de Ficha / Programa',
            'nivel': 'Nivel de Formación',
        }