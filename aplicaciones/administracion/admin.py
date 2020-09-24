from django.contrib import admin
from .models import Empresa,Establecimiento,Categoria,Producto,Usuario,Cliente,Combo,Carrito,Detalle_Carrito,Combo_Producto

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Establecimiento)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Combo)
admin.site.register(Carrito)
admin.site.register(Detalle_Carrito)
admin.site.register(Combo_Producto)

