from django import forms
from .models import Ficha

class FichaForm(forms.ModelForm):
    class Meta:
        model = Ficha
        fields = ['numero', 'programa', 'fecha_inicio', 'fecha_fin']
        
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 2993648'}),
            'programa': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'numero': 'Número de Ficha',
            'programa': 'Programa de Formación',
            'fecha_inicio': 'Fecha de Inicio Lectiva',
            'fecha_fin': 'Fecha de Fin Lectiva',
        }