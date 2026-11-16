from django.urls import path
from . import views
urlpatterns=[path('',views.inicio,name='inicio'),path('juegos/',views.catalogo,name='catalogo'),path('juegos/nuevo/',views.crear,name='crear'),path('juegos/<int:pk>/editar/',views.editar,name='editar'),path('juegos/<int:pk>/eliminar/',views.eliminar,name='eliminar'),path('movimientos/nuevo/',views.registrar,name='registrar'),path('movimientos/',views.historial,name='historial')]
