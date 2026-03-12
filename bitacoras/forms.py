from django import forms
from django.forms import inlineformset_factory
from .models import Bitacora, ActividadBitacora

class CrearBitacoraForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        # Excluimos los campos de control interno
        exclude = ['aprendiz_rel', 'numero_bitacora', 'estado', 'fecha_entrega_bitacora']
        
        widgets = {
            'clasificacion_informacion': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre_completo_aprendiz': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento_aprendiz': forms.Select(attrs={'class': 'form-select'}),
            'numero_identificacion_aprendiz': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_telefonico_aprendiz': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_institucional_aprendiz': forms.EmailInput(attrs={'class': 'form-control'}),
            'correo_personal_aprendiz': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion_residencia_aprendiz': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_grupo_ficha': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            'programa_formacion': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidad_ejecucion': forms.Select(attrs={'class': 'form-select'}),
            'exterior': forms.Select(attrs={'class': 'form-select'}),
            'pais_etapa': forms.TextInput(attrs={'class': 'form-control'}),
            'alternativa_etapa': forms.Select(attrs={'class': 'form-select'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nit_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'email_jefe': forms.EmailInput(attrs={'class': 'form-control'}),
            'nombre_instructor_seguimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'email_instructor_seguimiento': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_instructor_seguimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'arl_afiliado': forms.Select(attrs={'class': 'form-select'}),
            'nivel_riesgo': forms.Select(attrs={'class': 'form-select'}),
            'riesgo_corresponde': forms.Select(attrs={'class': 'form-select'}),
            'cuenta_epp': forms.Select(attrs={'class': 'form-select'}),
            'anexo_fotografico': forms.FileInput(attrs={'class': 'form-control'}),
            'firma_aprendiz': forms.FileInput(attrs={'class': 'form-control'}),
            'firma_jefe': forms.FileInput(attrs={'class': 'form-control'}),
            'firma_instructor': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.aprendiz = kwargs.pop('aprendiz', None)
        super().__init__(*args, **kwargs)
        if self.aprendiz:
            # Auto-llenado inicial
            self.fields['nombre_completo_aprendiz'].initial = self.aprendiz.usuario.get_full_name()
            self.fields['numero_identificacion_aprendiz'].initial = self.aprendiz.documento
            self.fields['contacto_telefonico_aprendiz'].initial = self.aprendiz.telefono
            self.fields['correo_institucional_aprendiz'].initial = self.aprendiz.usuario.email
            self.fields['numero_grupo_ficha'].initial = self.aprendiz.numero_ficha
            

# --- FORMULARIO PARA LAS ACTIVIDADES (TABLA DEL EXCEL) ---
class ActividadForm(forms.ModelForm):
    class Meta:
        model = ActividadBitacora
        fields = ['descripcion_actividad', 'competencias_asociadas', 'periodo_mes', 'evidencia_cumplimiento', 'observaciones']
        widgets = {
            'descripcion_actividad': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'competencias_asociadas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'periodo_mes': forms.TextInput(attrs={'class': 'form-control'}),
            'evidencia_cumplimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# --- FORMSET PARA MULTIPLES FILAS ---
ActividadFormSet = inlineformset_factory(Bitacora, ActividadBitacora, form=ActividadForm, extra=1, can_delete=True)