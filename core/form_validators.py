import re
from django import forms


def normalize_text(value):
    return (value or '').strip()


def validate_digits(value, label='campo', min_len=1, max_len=20):
    value = normalize_text(value)
    if not value.isdigit():
        raise forms.ValidationError(f'El campo "{label}" solo permite números (sin letras ni símbolos).')
    if len(value) < min_len or len(value) > max_len:
        raise forms.ValidationError(f'El campo "{label}" debe tener entre {min_len} y {max_len} dígitos.')
    return value


def validate_phone(value, label='teléfono', min_len=7, max_len=15, required=False):
    value = normalize_text(value)
    if not value:
        if required:
            raise forms.ValidationError(f'El campo "{label}" es obligatorio.')
        return value
    if not value.isdigit() or len(value) < min_len or len(value) > max_len:
        raise forms.ValidationError(f'El campo "{label}" debe tener entre {min_len} y {max_len} dígitos numéricos.')
    return value


def validate_person_name(value, label='nombre', min_len=2, max_len=70):
    value = normalize_text(value)
    if len(value) < min_len or len(value) > max_len:
        raise forms.ValidationError(f'El campo "{label}" debe tener entre {min_len} y {max_len} caracteres.')

    if re.search(r'\d', value):
        raise forms.ValidationError(f'El campo "{label}" no puede contener números.')

    # Permite letras, espacios, apóstrofe y guion.
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'\-]+", value):
        raise forms.ValidationError(f'El campo "{label}" contiene caracteres no válidos.')

    # Debe tener al menos dos letras reales
    if len(re.findall(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]', value)) < 2:
        raise forms.ValidationError(f'El campo "{label}" no parece un nombre válido.')

    return re.sub(r'\s+', ' ', value)


def validate_text_length(value, label='campo', min_len=1, max_len=70):
    value = normalize_text(value)
    if len(value) < min_len or len(value) > max_len:
        raise forms.ValidationError(f'El campo "{label}" debe tener entre {min_len} y {max_len} caracteres.')
    return value


def validate_email_length(value, max_len=70):
    value = normalize_text(value)
    if len(value) > max_len:
        raise forms.ValidationError(f'El correo no puede superar {max_len} caracteres.')
    return value
