# Generated by Django 5.1.6 on 2025-02-19 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Aplicacion1', '0005_carrito_itemcarrito'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicio',
            name='precio',
        ),
    ]
