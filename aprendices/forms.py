from django import forms
from .models import Aprendiz
from instructores.models import Instructor
from django.contrib.auth.models import User
from core.form_validators import (
    validate_digits,
    validate_email_length,
    validate_phone,
    validate_text_length,
)

PAIS_CHOICES = [
    ('Colombia', 'Colombia'),
    ('Argentina', 'Argentina'),
    ('Bolivia', 'Bolivia'),
    ('Brasil', 'Brasil'),
    ('Canadá', 'Canadá'),
    ('Chile', 'Chile'),
    ('Costa Rica', 'Costa Rica'),
    ('Ecuador', 'Ecuador'),
    ('España', 'España'),
    ('Estados Unidos', 'Estados Unidos'),
    ('Guatemala', 'Guatemala'),
    ('Honduras', 'Honduras'),
    ('México', 'México'),
    ('Panamá', 'Panamá'),
    ('Paraguay', 'Paraguay'),
    ('Perú', 'Perú'),
    ('República Dominicana', 'República Dominicana'),
    ('Uruguay', 'Uruguay'),
    ('Venezuela', 'Venezuela'),
    ('Otro', 'Otro'),
]

class AprendizForm(forms.ModelForm):
    etapa_exterior = forms.TypedChoiceField(
        choices=((False, 'No'), (True, 'Sí')),
        coerce=lambda x: str(x).lower() == 'true',
        empty_value=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    pais_etapa = forms.ChoiceField(choices=PAIS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo_personal'].widget.attrs['maxlength'] = 70
        self.fields['direccion_residencia'].widget.attrs['maxlength'] = 70
        self.fields['pais_etapa'].widget.attrs['maxlength'] = 70
        self.fields['departamento'].choices = [('', 'Seleccione un departamento...')]
        self.fields['ciudad_municipio'].choices = [('', 'Seleccione primero un departamento...')]

    def clean_documento(self):
        documento = validate_digits(self.cleaned_data.get('documento'), 'documento', min_len=6, max_len=20)
        if Aprendiz.objects.filter(documento=documento).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este documento ya está registrado en aprendices.')
        if Instructor.objects.filter(cedula=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado en instructores.')
        usuario_actual_id = self.instance.usuario_id if self.instance and self.instance.pk else None
        if User.objects.filter(username=documento).exclude(pk=usuario_actual_id).exists():
            raise forms.ValidationError('Este documento ya está registrado por otro usuario.')
        return documento

    def clean_telefono(self):
        return validate_phone(self.cleaned_data.get('telefono'), 'teléfono', min_len=7, max_len=15, required=False)

    def clean_correo_personal(self):
        return validate_email_length(self.cleaned_data.get('correo_personal'), max_len=70)

    def clean_direccion_residencia(self):
        return validate_text_length(self.cleaned_data.get('direccion_residencia'), 'dirección', min_len=5, max_len=70)

    def clean_departamento(self):
        return validate_text_length(self.cleaned_data.get('departamento'), 'departamento', min_len=2, max_len=70)

    def clean_ciudad_municipio(self):
        return validate_text_length(self.cleaned_data.get('ciudad_municipio'), 'ciudad o municipio', min_len=2, max_len=70)

    class Meta:
        model = Aprendiz
        exclude = ['usuario', 'programa_formacion']        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 1002345678',
                'inputmode': 'numeric',
                'pattern': '[0-9]*'
            }),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3001234567'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle 123 # 45-67'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'ciudad_municipio': forms.Select(attrs={'class': 'form-select'}),
            
            'numero_ficha': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            
            'modalidad_etapa': forms.Select(attrs={'class': 'form-select'}),
            'pais_etapa': forms.Select(attrs={'class': 'form-select'}),
            'etapa_exterior': forms.Select(attrs={'class': 'form-select'}), 
        }

    def clean(self):
        cleaned_data = super().clean()
        etapa_exterior = cleaned_data.get('etapa_exterior')
        pais_etapa = cleaned_data.get('pais_etapa')

        if etapa_exterior and not pais_etapa:
            self.add_error('pais_etapa', 'Debes seleccionar el país donde realiza la etapa.')
        if not etapa_exterior:
            cleaned_data['pais_etapa'] = 'Colombia'
        return cleaned_data
