from django.urls import path
from .views import *


urlpatterns = [	
	path('', inicio),	
	path('empresas/', getEmpresas),
	path('roles/',admin_rol),
]
