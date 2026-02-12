from django import forms
from django.forms import inlineformset_factory
from .models import Bitacora, ActividadBitacora
from instructores.models import Instructor
from fichas.models import Ficha

# --- 1. EL FORMULARIO PRINCIPAL (ENCABEZADO) ---
class CrearBitacoraForm(forms.ModelForm):
    # Campo especial para seleccionar la Ficha (Lista Desplegable)
    ficha = forms.ModelChoiceField(
        queryset=Ficha.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ficha de Caracterización",
        empty_label="-- Seleccione su Ficha --"
    )

    class Meta:
        model = Bitacora
        # Excluimos los campos que se llenan solos o que van en el formset
        exclude = [
            'aprendiz', 
            'numero_bitacora',  # Se calcula solo
            'estado', 
            'fecha_entrega', 
            'observaciones_instructor',
            # IMPORTANTE: Quitamos 'descripcion_actividades' y 'evidencia' de aquí
            # porque ahora las manejaremos en las filas dinámicas (abajo)
        ]
        
        widgets = {
            # FECHAS
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # SELECTORES (Listas desplegables)
            'instructor_seguimiento': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'afiliado_arl': forms.Select(attrs={'class': 'form-select'}),
            'nivel_riesgo': forms.Select(attrs={'class': 'form-select'}),
            'uso_epp': forms.Select(attrs={'class': 'form-select'}),
            
            # CAMPOS DE TEXTO (EMPRESA)
            'razon_social_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nit_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_jefe': forms.TextInput(attrs={'class': 'form-control'}),
            'email_jefe': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # 1. SACAMOS (pop) las variables personalizadas del diccionario kwargs
        # Si no hacemos esto, al llamar a super(), Django dará error porque no las reconoce.
        self.user = kwargs.pop('user', None)      # Sacamos 'user' si viene
        self.aprendiz = kwargs.pop('aprendiz', None) # Sacamos 'aprendiz' si viene
        
        # 2. Ahora que kwargs está "limpio", llamamos al constructor de Django
        super().__init__(*args, **kwargs)
        
        # 3. Configuraciones visuales y lógica
        self.fields['instructor_seguimiento'].label = "Instructor de Seguimiento"
        
        # LÓGICA DE AUTOCOMPLETADO
        # Usamos self.user o self.aprendiz dependiendo de qué nos mandó la vista
        usuario_a_consultar = self.user if self.user else (self.aprendiz.usuario if self.aprendiz else None)

        if usuario_a_consultar and hasattr(usuario_a_consultar, 'aprendiz'):
            aprendiz_obj = usuario_a_consultar.aprendiz
            ultima_bitacora = Bitacora.objects.filter(aprendiz=aprendiz_obj).last()
            
            if ultima_bitacora:
                # Pre-llenamos los datos si existen
                self.fields['razon_social_empresa'].initial = ultima_bitacora.razon_social_empresa
                self.fields['nit_empresa'].initial = ultima_bitacora.nit_empresa
                self.fields['direccion_empresa'].initial = ultima_bitacora.direccion_empresa
                self.fields['nombre_jefe'].initial = ultima_bitacora.nombre_jefe
                self.fields['cargo_jefe'].initial = ultima_bitacora.cargo_jefe
                self.fields['telefono_jefe'].initial = ultima_bitacora.telefono_jefe
                self.fields['email_jefe'].initial = ultima_bitacora.email_jefe
                self.fields['ficha'].initial = ultima_bitacora.ficha
                self.fields['instructor_seguimiento'].initial = ultima_bitacora.instructor_seguimiento


# --- 2. EL FORMULARIO PARA LAS FILAS (ACTIVIDADES) ---
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
            'evidencia': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre del archivo o evidencia'
            }),
        }

# --- 3. EL FORMSET (LA FÁBRICA DE FILAS) ---
# Esto crea la magia de "Agregar más filas"
ActividadFormSet = inlineformset_factory(
    Bitacora,               # Modelo Padre
    ActividadBitacora,      # Modelo Hijo
    form=ActividadForm,     # El formulario de la fila
    extra=1,                # Muestra 1 fila vacía al principio
    can_delete=True         # Permite borrar filas
)