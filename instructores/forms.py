from django import forms
from .models import Instructor
from aprendices.models import Aprendiz
from django.contrib.auth.models import User
from core.form_validators import (
    validate_digits,
    validate_email_length,
    validate_person_name,
    validate_phone,
    validate_text_length,
)

class InstructorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo_personal'].widget.attrs['maxlength'] = 70
        self.fields['direccion_residencia'].widget.attrs['maxlength'] = 70
        self.fields['profesion'].widget.attrs['maxlength'] = 70

    def clean_cedula(self):
        cedula = validate_digits(self.cleaned_data.get('cedula'), 'cédula', min_len=6, max_len=20)
        if Instructor.objects.filter(cedula=cedula).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este documento ya está registrado en instructores.')
        if Aprendiz.objects.filter(documento=cedula).exists():
            raise forms.ValidationError('Este documento ya está registrado en aprendices.')
        usuario_actual_id = self.instance.usuario_id if self.instance and self.instance.pk else None
        if User.objects.filter(username=cedula).exclude(pk=usuario_actual_id).exists():
            raise forms.ValidationError('Este documento ya está registrado por otro usuario.')
        return cedula

    def clean_telefono(self):
        return validate_phone(self.cleaned_data.get('telefono'), 'teléfono', min_len=7, max_len=15, required=False)

    def clean_correo_personal(self):
        return validate_email_length(self.cleaned_data.get('correo_personal'), max_len=70)

    def clean_direccion_residencia(self):
        return validate_text_length(self.cleaned_data.get('direccion_residencia'), 'dirección', min_len=5, max_len=70)

    def clean_profesion(self):
        profesion = validate_text_length(self.cleaned_data.get('profesion'), 'profesión', min_len=2, max_len=70)
        if profesion.isdigit():
            raise forms.ValidationError('La profesión no puede contener solo números.')
        return profesion

    class Meta:
        model = Instructor
        exclude = ['usuario']
        
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. 1002345678',
                'inputmode': 'numeric',
                'pattern': '[0-9]*'
            }),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 3001234567'}),
            'correo_personal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion_residencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle 123 # 45-67'}),
            
            'profesion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Ing. Eléctrico'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
        }
