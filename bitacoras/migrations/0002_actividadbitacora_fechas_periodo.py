from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitacoras', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actividadbitacora',
            name='periodo_mes',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='actividadbitacora',
            name='fecha_fin_actividad',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='actividadbitacora',
            name='fecha_inicio_actividad',
            field=models.DateField(blank=True, null=True),
        ),
    ]
