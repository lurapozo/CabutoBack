# Generated by Django 2.2.7 on 2023-02-18 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0107_canal_canalmensaje'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='nombreTarjeta',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='numeroTarjeta',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
