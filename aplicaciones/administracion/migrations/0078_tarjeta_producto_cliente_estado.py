# Generated by Django 2.2.7 on 2022-09-30 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0077_auto_20220930_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarjeta_producto_cliente',
            name='estado',
            field=models.CharField(default='A', max_length=1),
        ),
    ]
