from django.contrib import admin
from .models import Empresa,Establecimiento,Categoria,Producto,Usuario,Cliente

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Establecimiento)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(Cliente)
