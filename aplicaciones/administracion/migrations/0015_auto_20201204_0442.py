# Generated by Django 2.2.7 on 2020-12-04 04:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0014_auto_20201204_0437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrito',
            name='fecha_fin',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='carrito',
            name='fecha_inicio',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]