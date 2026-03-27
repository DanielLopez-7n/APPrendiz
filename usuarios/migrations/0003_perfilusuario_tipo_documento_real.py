from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_perfilusuario_tipo_documento'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='tipo_documento',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'No definido'),
                    ('CC', 'Cédula de Ciudadanía'),
                    ('TI', 'Tarjeta de Identidad'),
                    ('CE', 'Cédula de Extranjería'),
                    ('PEP', 'PEP'),
                    ('PAS', 'Pasaporte'),
                ],
                default='',
                help_text='Tipo de documento de identidad',
                max_length=5,
            ),
        ),
    ]
