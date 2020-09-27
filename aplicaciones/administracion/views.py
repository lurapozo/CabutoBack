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

def principalSuperAdmin(request):
	return render(request,'Principal/SuperAdmin_Principal.html')

def principalAdmin(request):
	return render(request,'Principal/Admin_Principal.html')

def empresas(request):
	return render(request,'Empresa/index.html')

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
