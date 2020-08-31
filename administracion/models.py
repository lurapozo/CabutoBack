from django.db import models
from datetime import datetime

# Create your models here.
class Empresa(models.Model):
	id_empresa = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=100)
	logo = models.BinaryField()
	razon_social=models.CharField(max_length=300)
	ruc_cedula=models.CharField(max_length=13)

def __str__(self):
	return self.nombre


class Establecimiento(models.Model):
	id_establecimiento=models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	direccion=models.CharField(max_length=100)
	telefono=models.CharField(max_length=100)
	latitud=models.FloatField()
	longitud=models.FloatField()
	encargado=models.CharField(max_length=100)
	image=models.BinaryField()
	estado=models.CharField(max_length=1)

def __str__(self):
	return self.nombre

class Categoria(models.Model):
	id_categoria=models.AutoField(primary_key=True)
	nombre = models.TextField()
	image=models.BinaryField()
	id_establecimiento=models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)

def __str__(self):
	return self.nombre

class Producto(models.Model):
	id_producto = models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	descripcion=models.CharField(max_length=100)
	precio=models.FloatField()
	image=models.BinaryField(blank = True, null = True)
	estado=models.CharField(max_length=1)
	id_categoria=models.ForeignKey(Categoria,on_delete=models.SET_NULL, null=True)

def __str__(self):
	return self.nombre

class Usuario(models.Model):
	id_usuario = models.AutoField(primary_key=True)
	username=models.CharField(max_length=100)
	cedula=models.CharField(max_length=100)
	correo=models.EmailField(max_length=100)
	contrasena=models.CharField(max_length=64)
	fecha_R=models.DateField(default=datetime.now)
	tipo_usuario=models.CharField(max_length=100,default="cliente")

def __str__(self):
	return self.username

class Cliente(models.Model):
	id_cliente = models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	apellido=models.CharField(max_length=100)
	metodo_pago= models.CharField(max_length=100)
	telefono =models.CharField(max_length=100)
	direccion = models.CharField(max_length=100)
	fecha_Nac=models.DateField()
	usuario = models.ForeignKey(Usuario,on_delete=models.SET_NULL,null=True)
	
def __str__(self):
	return '%s %s' %(self.nombre, self.apellido)
