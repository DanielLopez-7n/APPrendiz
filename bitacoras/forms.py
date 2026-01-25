from django import forms
from django.forms import inlineformset_factory
from .models import Bitacora, ActividadBitacora

# --- Formulario: Cabecera de la Bitácora ---
class BitacoraForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        # AGREGAMOS 'empresa' AQUÍ
        fields = ['empresa', 'numero', 'fecha_inicio', 'fecha_fin', 'modalidad']
        
        widgets = {
            # AGREGAMOS EL WIDGET PARA EMPRESA
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'empresa': 'Empresa Patrocinadora',
            'fecha_inicio': 'Fecha Inicio del Periodo',
            'fecha_fin': 'Fecha Fin del Periodo',
        }

# --- FormSet: Actividades (Tabla Dinámica) ---
# Este lo tenías perfecto, no le cambié nada.
ActividadFormSet = inlineformset_factory(
    Bitacora,             
    ActividadBitacora,    
    fields=['descripcion', 'fecha_ejecucion', 'evidencia'],
    widgets={
        'descripcion': forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'Describe detalladamente la actividad realizada...'
        }),
        'fecha_ejecucion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'evidencia': forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}),
    },
    extra=1,          
    can_delete=True   
)