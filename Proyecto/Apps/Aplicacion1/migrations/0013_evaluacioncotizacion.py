# Generated by Django 5.1.6 on 2025-02-23 23:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion1', '0012_cotizacion_insumos_alter_cotizacion_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluacionCotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insumos', models.TextField()),
                ('observaciones', models.TextField(blank=True, null=True)),
                ('tiempo_estimado', models.DecimalField(decimal_places=2, max_digits=5)),
                ('estimacion_costos', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_evaluacion', models.DateTimeField(auto_now_add=True)),
                ('cotizacion', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='evaluacion', to='Aplicacion1.cotizacion')),
            ],
        ),
    ]
