from django import forms
from .models import Ficha
from core.form_validators import validate_digits


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

    def clean_numero(self):
        return validate_digits(self.cleaned_data.get('numero'), 'número de ficha', min_len=3, max_len=20)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', 'La fecha fin debe ser mayor o igual a la fecha de inicio.')
        return cleaned_data
