from django import forms
from django.contrib.auth.models import User
from .models import Instructor

class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        # Añadimos 'usuario' para que Django pinte la lista desplegable
        fields = ['usuario', 'cedula', 'profesion', 'telefono', 'tipo_contrato']
        
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ing. de Sistemas'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'usuario': 'Vincular a Cuenta de Usuario (Previamente creada)',
            'cedula': 'Cédula de Ciudadanía',
        }

    # TRUCO: Filtrar la lista para mostrar solo usuarios disponibles
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos para que no salgan superusuarios, ni usuarios que ya son aprendices o instructores
        self.fields['usuario'].queryset = User.objects.filter(
            is_superuser=False, 
            instructor__isnull=True, 
            aprendiz__isnull=True
        )
        self.fields['usuario'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.username})"