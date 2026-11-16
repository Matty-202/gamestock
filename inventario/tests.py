from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User,Permission
from django.urls import reverse
from .models import Videojuego,Movimiento
class InventarioTests(TestCase):
 def setUp(self):
  self.user=User.objects.create_user(username='tester',password='ClaveSegura123!')
  self.user.user_permissions.add(Permission.objects.get(codename='add_movimiento'))
  self.client.login(username='tester',password='ClaveSegura123!')
  self.juego=Videojuego.objects.create(titulo='Juego prueba',plataforma='PC',genero='Acción',precio_compra=1000,precio_venta=2000,stock=3)
 def test_venta_descuenta_stock(self):
  response=self.client.post(reverse('registrar'),{'videojuego':self.juego.pk,'tipo':'VENTA','cantidad':2,'precio_unitario':'2000'})
  self.assertRedirects(response,reverse('historial'))
  self.juego.refresh_from_db();self.assertEqual(self.juego.stock,1)
  self.assertEqual(Movimiento.objects.count(),1)
 def test_venta_sin_stock_rechazada(self):
  response=self.client.post(reverse('registrar'),{'videojuego':self.juego.pk,'tipo':'VENTA','cantidad':4,'precio_unitario':'2000'})
  self.assertEqual(response.status_code,200)
  self.juego.refresh_from_db();self.assertEqual(self.juego.stock,3)
  self.assertEqual(Movimiento.objects.count(),0)
 def test_sin_login_redirige(self):
  self.client.logout();self.assertEqual(self.client.get(reverse('catalogo')).status_code,302)
 def test_sin_permiso_no_puede_crear(self):
  self.assertEqual(self.client.get(reverse('crear')).status_code,403)
 def test_compra_aumenta_stock(self):
  self.client.post(reverse('registrar'),{'videojuego':self.juego.pk,'tipo':'COMPRA','cantidad':5,'precio_unitario':'1000'})
  self.juego.refresh_from_db();self.assertEqual(self.juego.stock,8)
