from django import forms
from django.contrib.auth.models import User
from .models import Aprendiz

class AprendizForm(forms.ModelForm):
    class Meta:
        model = Aprendiz
        fields = ['usuario', 'documento', 'numero_ficha', 'programa_formacion', 'telefono']
        
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'numero_ficha': forms.Select(attrs={'class': 'form-select'}),
            'programa_formacion': forms.Select(attrs={'class': 'form-select'}),
            
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula o T.I'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'usuario': 'Vincular a Cuenta de Usuario (Previamente creada)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].queryset = User.objects.filter(is_superuser=False, aprendiz__isnull=True)
        self.fields['usuario'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.username})"