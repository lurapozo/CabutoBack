from django.contrib import admin
from .models import Empresa,Establecimiento,Categoria,Producto

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Establecimiento)
admin.site.register(Categoria)
admin.site.register(Producto)