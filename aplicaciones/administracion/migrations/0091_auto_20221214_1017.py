# Generated by Django 2.2.7 on 2022-12-14 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0090_auto_20221210_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarjeta_monto_cliente',
            name='fecha',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='tarjeta_producto_cliente',
            name='fecha',
            field=models.DateTimeField(null=True),
        ),
    ]
