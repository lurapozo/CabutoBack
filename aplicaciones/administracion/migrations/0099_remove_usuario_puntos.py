# Generated by Django 2.2.7 on 2023-01-27 06:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0098_cliente_puntos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='puntos',
        ),
    ]
