from django import forms
from django.forms import inlineformset_factory
from .models import Bitacora, ActividadBitacora
from django.contrib.auth.models import User

# --- FORMULARIO PRINCIPAL DE LA BITÁCORA ---
class CrearBitacoraForm(forms.ModelForm):
    # Convertimos el campo de texto a un desplegable de usuarios (instructores)
    nombre_instructor_seguimiento = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True, is_active=True, is_superuser=False),
        empty_label="Seleccione un instructor asignado...",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Instructor de Seguimiento"
    )

    class Meta:
        model = Bitacora
        exclude = ['aprendiz_rel', 'numero_bitacora', 'estado', 'fecha_entrega_bitacora']
        
        widgets = {
            'clasificacion_informacion': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # --- Auto-llenado bloqueado (solo lectura) ---
            'nombre_completo_aprendiz': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'tipo_documento_aprendiz': forms.Select(attrs={'class': 'form-select'}),
            'numero_identificacion_aprendiz': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'contacto_telefonico_aprendiz': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_institucional_aprendiz': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'correo_personal_aprendiz': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion_residencia_aprendiz': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_grupo_ficha': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_ejecucion': forms.Select(attrs={'class': 'form-select'}),
            'exterior': forms.Select(attrs={'class': 'form-select'}),
            'pais_etapa': forms.TextInput(attrs={'class': 'form-control'}),
            'alternativa_etapa': forms.Select(attrs={'class': 'form-select'}),
            
            # --- Empresa ---
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nit_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'email_jefe': forms.EmailInput(attrs={'class': 'form-control'}),
            
            # --- Instructor (Auto-llenado por AJAX) ---
            'email_instructor_seguimiento': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'telefono_instructor_seguimiento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            
            # --- SST y Firmas ---
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
            # 1. AUTO-LLENADO BÁSICO DEL APRENDIZ
            self.fields['nombre_completo_aprendiz'].initial = self.aprendiz.usuario.get_full_name()
            self.fields['numero_identificacion_aprendiz'].initial = self.aprendiz.documento
            self.fields['contacto_telefonico_aprendiz'].initial = self.aprendiz.telefono
            self.fields['correo_institucional_aprendiz'].initial = self.aprendiz.usuario.email
            
            if hasattr(self.aprendiz, 'numero_ficha'):
                ficha = getattr(self.aprendiz, 'numero_ficha', None)
                if ficha:
                    # Solo el número en "Número de grupo / ficha"
                    self.fields['numero_grupo_ficha'].initial = ficha.numero
                    # El nombre del programa en "Programa de formación"
                    if getattr(ficha, 'programa', None):
                        self.fields['programa_formacion'].initial = ficha.programa.nombre

            # 2. AUTO-LLENADO DE EMPRESA (Busca la bitácora anterior)
            ultima_bitacora = Bitacora.objects.filter(aprendiz_rel=self.aprendiz).order_by('-id').first()
            if ultima_bitacora and not self.instance.pk: 
                self.fields['nombre_empresa'].initial = ultima_bitacora.nombre_empresa
                self.fields['nit_empresa'].initial = ultima_bitacora.nit_empresa
                self.fields['direccion_empresa'].initial = ultima_bitacora.direccion_empresa
                self.fields['nombre_jefe'].initial = ultima_bitacora.nombre_jefe
                self.fields['cargo_jefe'].initial = ultima_bitacora.cargo_jefe
                self.fields['telefono_jefe'].initial = ultima_bitacora.telefono_jefe
                self.fields['email_jefe'].initial = ultima_bitacora.email_jefe
                self.fields['modalidad_formacion'].initial = ultima_bitacora.modalidad_formacion
                self.fields['modalidad_ejecucion'].initial = ultima_bitacora.modalidad_ejecucion

    def clean_numero_identificacion_aprendiz(self):
        documento = (self.cleaned_data.get('numero_identificacion_aprendiz') or '').strip()
        if documento and not documento.isdigit():
            raise forms.ValidationError(
                'El número de identificación del aprendiz solo permite números (sin letras ni símbolos).'
            )
        if documento and (len(documento) < 6 or len(documento) > 20):
            raise forms.ValidationError('El número de identificación debe tener entre 6 y 20 dígitos.')
        return documento


# --- FORMULARIO PARA LAS ACTIVIDADES ---
class ActividadForm(forms.ModelForm):
    class Meta:
        model = ActividadBitacora
        fields = [
            'descripcion_actividad',
            'competencias_asociadas',
            'fecha_inicio_actividad',
            'fecha_fin_actividad',
            'evidencia_cumplimiento',
            'observaciones'
        ]
        widgets = {
            'descripcion_actividad': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'competencias_asociadas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fecha_inicio_actividad': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin_actividad': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # 🔥 AQUÍ ESTÁ EL TRUCO: Forzamos a que sea un input type="file"
            'evidencia_cumplimiento': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf,.doc,.docx'}),
            
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio_actividad')
        fecha_fin = cleaned_data.get('fecha_fin_actividad')

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin_actividad', 'La fecha fin debe ser mayor o igual a la fecha inicio.')

        return cleaned_data
# --- FORMSET PARA MULTIPLES FILAS ---
ActividadFormSet = inlineformset_factory(Bitacora, ActividadBitacora, form=ActividadForm, extra=1, can_delete=True)
