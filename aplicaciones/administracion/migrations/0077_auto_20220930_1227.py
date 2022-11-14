# Generated by Django 2.2.7 on 2022-09-30 17:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0076_tarjeta_monto_cliente_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tarjeta_Producto_Cliente',
            fields=[
                ('id_tarjetaxcliente', models.AutoField(primary_key=True, serialize=False)),
                ('id_cliente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Cliente')),
            ],
        ),
        migrations.RemoveField(
            model_name='tarjeta_producto',
            name='id_usuario',
        ),
        migrations.AddField(
            model_name='tarjeta_producto',
            name='id_cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Cliente'),
        ),
        migrations.DeleteModel(
            name='Tarjeta_Producto_Usuario',
        ),
        migrations.AddField(
            model_name='tarjeta_producto_cliente',
            name='id_tarjeta',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administracion.Tarjeta_Producto'),
        ),
    ]