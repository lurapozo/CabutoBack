# Generated by Django 2.2.7 on 2023-01-27 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0100_auto_20230127_0852'),
    ]

    operations = [
        migrations.CreateModel(
            name='Premios',
            fields=[
                ('id_premio', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='')),
                ('descripcion', models.CharField(max_length=300)),
                ('cantidad', models.IntegerField()),
                ('puntos', models.IntegerField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
            ],
        ),
    ]
