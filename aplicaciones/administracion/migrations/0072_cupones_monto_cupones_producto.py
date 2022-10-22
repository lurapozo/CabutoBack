# Generated by Django 2.2.7 on 2022-09-23 01:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0071_cupones_tipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cupones_Producto',
            fields=[
                ('id_cuponesproducto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
                ('cantidad', models.IntegerField(default=1)),
                ('id_cupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Cupones')),
                ('id_producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='Cupones_Monto',
            fields=[
                ('id_cuponesmonto', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
                ('monto', models.FloatField()),
                ('id_cupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Cupones')),
            ],
        ),
    ]
