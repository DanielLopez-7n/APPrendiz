from django import forms
from .models import Instructor
from aprendices.models import Aprendiz
from django.contrib.auth.models import User

class InstructorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo_personal'].widget.attrs['maxlength'] = 70
        self.fields['direccion_residencia'].widget.attrs['maxlength'] = 70
        self.fields['profesion'].widget.attrs['maxlength'] = 70

    def clean_cedula(self):
        cedula = (self.cleaned_data.get('cedula') or '').strip()
        if not cedula.isdigit():
            raise forms.ValidationError('La cédula solo permite números (sin letras ni símbolos).')
        if len(cedula) < 6 or len(cedula) > 20:
            raise forms.ValidationError('La cédula debe tener entre 6 y 20 dígitos.')
        if Instructor.objects.filter(cedula=cedula).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este documento ya está registrado en instructores.')
        if Aprendiz.objects.filter(documento=cedula).exists():
            raise forms.ValidationError('Este documento ya está registrado en aprendices.')
        usuario_actual_id = self.instance.usuario_id if self.instance and self.instance.pk else None
        if User.objects.filter(username=cedula).exclude(pk=usuario_actual_id).exists():
            raise forms.ValidationError('Este documento ya está registrado por otro usuario.')
        return cedula

    def clean_telefono(self):
        telefono = (self.cleaned_data.get('telefono') or '').strip()
        if telefono and (not telefono.isdigit() or len(telefono) < 7 or len(telefono) > 15):
            raise forms.ValidationError('El teléfono debe tener entre 7 y 15 dígitos numéricos.')
        return telefono

    def clean_correo_personal(self):
        correo = (self.cleaned_data.get('correo_personal') or '').strip()
        if len(correo) > 70:
            raise forms.ValidationError('El correo personal no puede superar 70 caracteres.')
        return correo

    def clean_direccion_residencia(self):
        direccion = (self.cleaned_data.get('direccion_residencia') or '').strip()
        if len(direccion) > 70:
            raise forms.ValidationError('La dirección no puede superar 70 caracteres.')
        return direccion

    def clean_profesion(self):
        profesion = (self.cleaned_data.get('profesion') or '').strip()
        if len(profesion) > 70:
            raise forms.ValidationError('La profesión no puede superar 70 caracteres.')
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
