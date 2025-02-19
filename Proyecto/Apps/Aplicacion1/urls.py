
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('reg_clientes/', views.reg_clientes, name='reg_clientes'),
    path('login_empleados/', views.login_empleados, name='login_empleados'),
    path('login_clientes/', views.login_clientes, name='login_clientes'),
    path('reg_productos/', views.reg_productos, name='reg_productos'),
    path('reg_servicios/', views.reg_servicios, name='reg_servicios'),
    path('agregar_al_carrito/<int:id_producto>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('eliminar_item_carrito/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),

]

