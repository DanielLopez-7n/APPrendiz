from django import forms
from .models import Empresa
from core.form_validators import (
    validate_digits,
    validate_email_length,
    validate_person_name,
    validate_phone,
    validate_text_length,
)


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nit', 'nombre', 'direccion', 'telefono', 'encargado', 'email_encargado']

        widgets = {
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 9001234567'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa S.A.S'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección física'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'encargado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del jefe inmediato'}),
            'email_encargado': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@empresa.com'}),
        }

        labels = {
            'nit': 'NIT de la Empresa',
            'nombre': 'Razón Social',
            'encargado': 'Nombre del Jefe Inmediato',
            'email_encargado': 'Correo Electrónico (Jefe)',
        }

    def clean_nit(self):
        nit = (self.cleaned_data.get('nit') or '').replace('.', '').replace('-', '').strip()
        return validate_digits(nit, 'NIT', min_len=6, max_len=15)

    def clean_nombre(self):
        nombre = validate_text_length(self.cleaned_data.get('nombre'), 'razón social', min_len=3, max_len=70)
        if nombre.isdigit():
            raise forms.ValidationError('La razón social no puede contener solo números.')
        return nombre

    def clean_direccion(self):
        return validate_text_length(self.cleaned_data.get('direccion'), 'dirección', min_len=5, max_len=120)

    def clean_telefono(self):
        return validate_phone(self.cleaned_data.get('telefono'), 'teléfono', min_len=7, max_len=15, required=False)

    def clean_encargado(self):
        return validate_person_name(self.cleaned_data.get('encargado'), 'jefe inmediato', min_len=3, max_len=70)

    def clean_email_encargado(self):
        return validate_email_length(self.cleaned_data.get('email_encargado'), max_len=70)
