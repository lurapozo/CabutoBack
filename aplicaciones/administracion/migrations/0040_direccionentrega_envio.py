# Generated by Django 2.2.7 on 2021-02-03 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0039_detalle_pedido_pedido_zonaenvio'),
    ]

    operations = [
        migrations.AddField(
            model_name='direccionentrega',
            name='envio',
            field=models.FloatField(default=2),
            preserve_default=False,
        ),
    ]
