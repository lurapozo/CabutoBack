# Generated by Django 2.2.7 on 2020-10-27 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0002_auto_20201027_0040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.CharField(default='cliente', max_length=150),
        ),
    ]