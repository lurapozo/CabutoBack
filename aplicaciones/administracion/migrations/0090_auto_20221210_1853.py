# Generated by Django 2.2.7 on 2022-12-10 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0089_usuario_codigo_unico'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarjeta_monto_cliente',
            name='fecha',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='tarjeta_producto_cliente',
            name='fecha',
            field=models.DateField(null=True),
        ),
    ]
