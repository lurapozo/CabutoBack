from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
import requests
import json
import random
from django.core import serializers
from .models import *

# Create your views here.

def inicio(request):
	return render(request, 'Login/login.html')


def getProducto(request):
	if request.method == 'GET':
		res = []
		print(request.GET.get("nombre"))
		

		if request.GET.get("nombre")!=None:
			res = []
			valor = request.GET.get("nombre")
			print("lo que recibe mi get :v ay diosito que reaccione",valor, str(valor))
			producto= Producto.objects.filter(nombre__icontains=str(valor))
			#producto= Producto.objects.filter()
			for product in producto:
				print(product)
				print(product.id_producto)

				diccionario={"id":product.id_producto,"nombre":product.nombre,"descripcion":product.descripcion,"precio":product.precio,"estado":product.estado}
				res.append(diccionario)
				#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
			print("hay un get")
			print(res)
			return JsonResponse(res,safe=False)
		else:
			#id = request.GET.get("id_producto")
			#producto= Producto.objects.filter(id_categoria_id=1)
			producto= Producto.objects.filter()
			for product in producto:
				#print(product)
				#print(product.id_producto)

				diccionario={"id":product.id_producto,"nombre":product.nombre,"descripcion":product.descripcion,"precio":product.precio,"estado":product.estado}
				res.append(diccionario)
				#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
		#	print("hay un get")
		#	print(res)
			#json_convert= simplejson.dumps({lista_producto:res})
			

			return JsonResponse(res,safe=False)

	return HttpResponse(status=400)

def getProductoAaZ(request):
	if request.method=='GET':
		res=[]
		producto=Producto.objects.filter().order_by('nombre')
		for product in producto:
			diccionario={"id":product.id_producto,"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
			res.append(diccionario)
			#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
		print("hay un get")
		print(res)
		return JsonResponse(res,safe=False)
	return HttpResponse(status=400)


def getProductoZaA(request):
	if request.method=='GET':
		res=[]
		producto=Producto.objects.filter().order_by('-nombre')
		for product in producto:
			diccionario={"id":product.id_producto,"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
			res.append(diccionario)
			#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
		print("hay un get")
		print(res)
		return JsonResponse(res,safe=False)
	return HttpResponse(status=400)

def getProductoPrecioMenor(request):
	if request.method=='GET':
		res=[]
		producto=Producto.objects.filter().order_by('-precio')
		for product in producto:
			diccionario={"id":product.id_producto,"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
			res.append(diccionario)
			#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
		print("hay un get")
		print(res)
		return JsonResponse(res,safe=False)
	return HttpResponse(status=400)

def getProductoPrecioMayor(request):
	if request.method=='GET':
		res=[]
		producto=Producto.objects.filter().order_by('precio')
		for product in producto:
			diccionario={"id":product.id_producto,"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
			res.append(diccionario)
			#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
		print("hay un get")
		print(res)
		return JsonResponse(res,safe=False)
	return HttpResponse(status=400)


@csrf_exempt
def registro(request):
	if request.method == 'POST':
		print("estoy en django, metodo registro ")
		response = json.loads(request.body)
		print(response)
		cedula = response["cedula"]
		email = response['email']
		contra =response['contrasena']
		contraR = response['confirmar']
		##if contraR != contra:
		##	return return HttpResponse(status=400)
		nombre = response['nombre']
		apellido = response['apellido']
		u =Usuario(cedula=cedula,correo=email,contrasena=contra)
		u.save()
		u2=Usuario.objects.filter().values()
		c = Cliente(nombre=nombre,apellido=apellido,usuario=u)
		c.save()
		response_data = {
				'valid': 'OK'
				}
		return JsonResponse(response_data,safe=False)


	response_data = {
		'valid': 'NOT'
		}
	return JsonResponse(response_data,safe=False)
	#else
		#print("algo salio mal")
		#return render(response,"/register")


@csrf_exempt
def login(request):

	if request.method == 'POST':
		print("estoy en django, metodo registro ")
		response = json.loads(request.body)
		print(response)
		email = response['correo']
		contra =response['contrasena']
		users = Usuario.objects.filter()
		print(users)
		for u in users :
			c = u.correo
			cn = u.contrasena
			if c == email and cn == contra:
				response_data = {
				'valid': 'OK'
				}
				return JsonResponse(response_data,safe=False)


	response_data = {
		'valid': 'NOT'
		}
	return JsonResponse(response_data,safe=False)


def getEmpresas(request):
	if request.method=='GET':
		res=[]
		
		empresas=Empresa.objects.all()
		for emp in empresas:
			dicc={"id":emp.id_empresa,"nombre":emp.nombre,"descripcion":emp.descripcion,"razon_social":emp.razon_social,"ruc_cedula":emp.ruc_cedula}
			res.append(dicc)
		return JsonResponse(res,safe=False)
	return HttpResponse(status=400)


def admin_rol(request):
	paquete = []
	return render(request, "roles/admin_rol.html", paquete)
