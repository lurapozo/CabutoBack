# Generated by Django 2.2.7 on 2020-12-04 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0013_auto_20201204_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrito',
            name='fecha_fin',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='carrito',
            name='fecha_inicio',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
