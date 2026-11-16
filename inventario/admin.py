from django.contrib import admin
from .models import Videojuego,Movimiento
@admin.register(Videojuego)
class VideojuegoAdmin(admin.ModelAdmin):
 list_display=['titulo','plataforma','genero','stock','precio_compra','precio_venta'];search_fields=['titulo','genero'];list_filter=['plataforma']
@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
 list_display=['videojuego','tipo','cantidad','precio_unitario','usuario','fecha'];list_filter=['tipo','fecha'];readonly_fields=['videojuego','tipo','cantidad','precio_unitario','usuario','fecha']
 def has_add_permission(self,request):return False
 def has_change_permission(self,request,obj=None):return False
 def has_delete_permission(self,request,obj=None):return False
