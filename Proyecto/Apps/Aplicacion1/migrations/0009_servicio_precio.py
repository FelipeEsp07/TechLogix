# Generated by Django 5.1.6 on 2025-02-20 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion1', '0008_cotizacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='precio',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
