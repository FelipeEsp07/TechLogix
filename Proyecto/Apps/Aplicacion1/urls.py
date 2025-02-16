
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reg_clientes/', views.reg_clientes, name='reg_clientes'),
    path('login_empleados/', views.login_empleados, name='login_empleados'),
    path('login_clientes/', views.login_clientes, name='login_clientes'),
]

