from django import forms
from .models import Aprendiz

class AprendizForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo_personal'].widget.attrs['maxlength'] = 70
        self.fields['direccion_residencia'].widget.attrs['maxlength'] = 70
        self.fields['pais_etapa'].widget.attrs['maxlength'] = 70

    def clean_documento(self):
        documento = (self.cleaned_data.get('documento') or '').strip()
        if not documento.isdigit():
            raise forms.ValidationError('El documento solo permite números (sin letras ni símbolos).')
        if len(documento) < 6 or len(documento) > 20:
            raise forms.ValidationError('El documento debe tener entre 6 y 20 dígitos.')
        return documento

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
            
            'numero_ficha': forms.Select(attrs={'class': 'form-select'}),
            'modalidad_formacion': forms.Select(attrs={'class': 'form-select'}),
            
            'modalidad_etapa': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. SENA, Microsoft...'}),
            'pais_etapa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Colombia'}),
            # Al checkbox le ponemos la clase especial form-check-input
            'etapa_exterior': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }
