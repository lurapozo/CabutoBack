from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import requests
from .models import *

# Create your views here.


def getProducto(request):
	if request.method == 'GET':
		res = []
		#id = request.GET.get("id_producto")
		#producto= Producto.objects.filter(id_categoria_id=1)
		producto= Producto.objects.filter()
		for product in producto:
			print(product)
			print(product.id_producto)

			diccionario={"id":product.id_producto,"nombre":product.nombre,"descripcion":product.descripcion,"precio":product.precio,"estado":product.estado}
			res.append(diccionario)
			#res[product.id_producto]={"nombre":product.nombre,"precio":product.precio, "estado":product.estado}
		print("hay un get")
		print(res)
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
