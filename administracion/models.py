import secrets
import random
from datetime import datetime
from django.db import models
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django import forms

# Create your models here.

class Usuario(models.Model):
	id_usuario = models.AutoField(primary_key=True)
	username=models.CharField(max_length=100,default = "NULL")
	cedula=models.CharField(max_length=10)
	correo=models.EmailField(unique=True)
	contrasena=models.CharField(max_length=64)
	def __str__(self):
		return self.username




class Empresa(models.Model):
	id_empresa = models.AutoField(primary_key=True)
	nombre = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=100)
	logo = models.ImageField()
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
	image=models.ImageField()
	estado=models.CharField(max_length=1)
	def __str__(self):
		return self.nombre



class Categoria(models.Model):
	id_categoria=models.AutoField(primary_key=True)
	nombre = models.TextField()
	image=models.ImageField()
	id_establecimiento=models.ForeignKey(Establecimiento,on_delete=models.SET_NULL, null=True)
	def __str__(self):
		return self.nombre



class Producto(models.Model):
	id_producto = models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	descripcion=models.CharField(max_length=100)
	precio=models.FloatField()
	image=models.ImageField()
	estado=models.CharField(max_length=1)
	id_categoria=models.ForeignKey(Categoria,on_delete=models.SET_NULL, null=True)
	def __str__(self):
		return self.nombre







class Cliente(models.Model):
	id_cliente = models.AutoField(primary_key=True)
	nombre=models.CharField(max_length=100)
	apellido=models.CharField(max_length=100)
	metodo_pago= models.CharField(max_length=100, default = "Efectivo")
	telefono =models.CharField(max_length=100, default = "NONE")
	direccion = models.CharField(max_length=100, default = "NONE")
	fecha_Nac=models.DateField(default=datetime.now)
	usuario = models.ForeignKey(Usuario,on_delete=models.SET_NULL,null=True)
	def __str__(self):
		return '%s %s' %(self.nombre, self.apellido)
	

