from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import requests
from .models import *

# Create your views here.


def getProducto(request):
	print("aqui hay un get")
	if request.method == 'GET':
		res = dict()
		#id = request.GET.get("id_producto")
		#producto= Producto.objects.filter(id_categoria_id=1)
		producto= Producto.objects.filter()
		#print(request)
		for product in producto:
			print(product)
			res[product.nombre]={"precio":product.precio, "estado":product.estado}
		print("hay un get")
		print(res)

		return JsonResponse(res)
	return HttpResponse(status=404)

