# Generated by Django 5.1.6 on 2025-02-23 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion1', '0011_producto_imagen_servicio_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizacion',
            name='insumos',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cotizacion',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('visita_programada', 'Visita Programada'), ('evaluado', 'Evaluado'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')], default='pendiente', max_length=20),
        ),
    ]
