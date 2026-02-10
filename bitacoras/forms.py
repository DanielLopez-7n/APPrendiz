# bitacoras/forms.py

from django import forms
from .models import Bitacora
from instructores.models import Instructor

class CrearBitacoraForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        fields = [
            'numero_bitacora',
            'fecha_inicio', 'fecha_fin',
            'instructor_seguimiento', # Esto será una lista desplegable automática
            'razon_social_empresa', 'nit_empresa', 'direccion_empresa',
            'nombre_jefe_inmediato', 'cargo_jefe', 'telefono_jefe', 'email_jefe',
            'modalidad', 'pais_etapa',
            'afiliado_arl', 'nivel_riesgo', 'riesgo_corresponde', 'uso_epp',
            'descripcion_actividades',
            'archivo_evidencia'
        ]
        widgets = {
            # FECHAS (Calendario)
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # SELECTORES (Listas desplegables)
            'instructor_seguimiento': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'afiliado_arl': forms.Select(attrs={'class': 'form-select'}),
            'nivel_riesgo': forms.Select(attrs={'class': 'form-select'}),
            'riesgo_corresponde': forms.Select(attrs={'class': 'form-select'}),
            'uso_epp': forms.Select(attrs={'class': 'form-select'}),
            
            # TEXTO (Inputs normales con estilo Bootstrap)
            'numero_bitacora': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'razon_social_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nit_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_jefe_inmediato': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'email_jefe': forms.EmailInput(attrs={'class': 'form-control'}),
            'pais_etapa': forms.TextInput(attrs={'class': 'form-control', 'value': 'Colombia'}),
            
            # ÁREA DE TEXTO GRANDE
            'descripcion_actividades': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describa las actividades realizadas en este periodo...'}),
            'archivo_evidencia': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Recibimos el aprendiz para intentar pre-llenar datos si ya hizo bitácoras antes
        aprendiz = kwargs.pop('aprendiz', None)
        super().__init__(*args, **kwargs)
        
        # Etiqueta amigable para el instructor
        self.fields['instructor_seguimiento'].label = "Seleccione su Instructor"
        self.fields['instructor_seguimiento'].queryset = Instructor.objects.all() # Aquí podrías filtrar si quisieras

        # Lógica de "Autocompletar" (Si ya existe una bitácora anterior)
        if aprendiz:
            ultima_bitacora = Bitacora.objects.filter(aprendiz=aprendiz).last()
            if ultima_bitacora:
                # Pre-llenamos los datos de la empresa y el instructor para que no los escriba de nuevo
                self.fields['razon_social_empresa'].initial = ultima_bitacora.razon_social_empresa
                self.fields['nit_empresa'].initial = ultima_bitacora.nit_empresa
                self.fields['direccion_empresa'].initial = ultima_bitacora.direccion_empresa
                self.fields['nombre_jefe_inmediato'].initial = ultima_bitacora.nombre_jefe_inmediato
                self.fields['cargo_jefe'].initial = ultima_bitacora.cargo_jefe
                self.fields['telefono_jefe'].initial = ultima_bitacora.telefono_jefe
                self.fields['email_jefe'].initial = ultima_bitacora.email_jefe
                self.fields['instructor_seguimiento'].initial = ultima_bitacora.instructor_seguimiento
                self.fields['nivel_riesgo'].initial = ultima_bitacora.nivel_riesgo