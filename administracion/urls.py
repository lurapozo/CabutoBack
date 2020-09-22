from django.urls import path
from .views import *


urlpatterns = [
	path('producto/', getProducto),
	path('producto/orderAsc', getProductoAaZ),
	path('producto/orderDesc',getProductoZaA),
	path('producto/precioMenor', getProductoPrecioMenor),
	path('producto/precioMayor', getProductoPrecioMayor),
	path('registro/', registro),
	path('login/,login),
	path('empresas/', getEmpresas),
	path('roles/',admin_rol),



]
