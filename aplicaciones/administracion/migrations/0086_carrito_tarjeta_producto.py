# Generated by Django 2.2.7 on 2022-10-09 23:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0085_auto_20221009_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrito_Tarjeta_Producto',
            fields=[
                ('id_carritoxtarjeta', models.AutoField(primary_key=True, serialize=False)),
                ('precio', models.FloatField(default=0)),
                ('id_carrito', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Carrito')),
                ('id_tarjeta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Tarjeta_Producto')),
            ],
        ),
    ]