from django import forms
from django.forms import inlineformset_factory
from .models import Bitacora, ActividadBitacora
from instructores.models import Instructor
from fichas.models import Ficha
from empresas.models import Empresa  # Importación del modelo relacionado

# --- 1. FORMULARIO PRINCIPAL (ENCABEZADO DE BITÁCORA) ---
class CrearBitacoraForm(forms.ModelForm):
    # Campo relacional para la selección de la Ficha de Caracterización
    ficha = forms.ModelChoiceField(
        queryset=Ficha.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ficha de Caracterización",
        empty_label="-- Seleccione su Ficha --"
    )

    # Campo relacional para la selección del Ente Co-formador
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ente Co-formador (Empresa)",
        empty_label="-- Seleccione la Empresa --"
    )

    class Meta:
        model = Bitacora
        # Exclusión de campos autogenerados o gestionados mediante formsets anidados
        exclude = [
            'aprendiz', 
            'numero_bitacora',
            'estado', 
            'fecha_entrega', 
            'observaciones_instructor',
        ]
        
        widgets = {
            # Campos de tipo Fecha
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Campos de selección estándar
            'instructor_seguimiento': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'afiliado_arl': forms.Select(attrs={'class': 'form-select'}),
            'nivel_riesgo': forms.Select(attrs={'class': 'form-select'}),
            'uso_epp': forms.Select(attrs={'class': 'form-select'}),
            
            # Campos de texto (Datos de contacto del jefe inmediato)
            'nombre_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'email_jefe': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Extracción de argumentos personalizados previos a la inicialización de la clase padre
        self.user = kwargs.pop('user', None)
        self.aprendiz = kwargs.pop('aprendiz', None)
        
        super().__init__(*args, **kwargs)
        
        # Configuraciones visuales adicionales
        self.fields['instructor_seguimiento'].label = "Instructor de Seguimiento"
        
        # Lógica de autocompletado basada en el histórico del usuario
        usuario_a_consultar = self.user if self.user else (self.aprendiz.usuario if self.aprendiz else None)

        if usuario_a_consultar and hasattr(usuario_a_consultar, 'aprendiz'):
            aprendiz_obj = usuario_a_consultar.aprendiz
            ultima_bitacora = Bitacora.objects.filter(aprendiz=aprendiz_obj).last()
            
            if ultima_bitacora:
                # Carga de valores iniciales correspondientes al último registro válido
                self.fields['empresa'].initial = ultima_bitacora.empresa
                self.fields['nombre_jefe'].initial = ultima_bitacora.nombre_jefe
                self.fields['cargo_jefe'].initial = ultima_bitacora.cargo_jefe
                self.fields['telefono_jefe'].initial = ultima_bitacora.telefono_jefe
                self.fields['email_jefe'].initial = ultima_bitacora.email_jefe
                self.fields['ficha'].initial = ultima_bitacora.ficha
                self.fields['instructor_seguimiento'].initial = ultima_bitacora.instructor_seguimiento


# --- 2. FORMULARIO PARA REGISTROS HIJOS (ACTIVIDADES) ---
class ActividadForm(forms.ModelForm):
    class Meta:
        model = ActividadBitacora
        fields = ['descripcion', 'fecha_ejecucion', 'evidencia']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Describa la actividad realizada...'
            }),
            'fecha_ejecucion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'evidencia': forms.FileInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre del archivo o evidencia'
            }),
        }

# --- 3. CONFIGURACIÓN DEL INLINE FORMSET ---
# Instanciación de la fábrica de formularios dinámicos para el modelo ActividadBitacora
ActividadFormSet = inlineformset_factory(
    Bitacora,
    ActividadBitacora,
    form=ActividadForm,
    extra=1,
    can_delete=True
)