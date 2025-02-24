
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('reg_clientes/', views.reg_clientes, name='reg_clientes'),
    path('reg_empleados/', views.reg_empleados, name='reg_empleados'),
    path('login_clientes/', views.login_clientes, name='login_clientes'),
    path('reg_productos/', views.reg_productos, name='reg_productos'),
    path('reg_servicios/', views.reg_servicios, name='reg_servicios'),
    path('agregar_al_carrito/<int:id_producto>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='carrito'),
    path('eliminar_item_carrito/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('cotizaciones/', views.cotizaciones_view, name='cotizaciones'),
    path('cotizaciones/confirmar/', views.confirmar_cotizacion, name='confirmar_cotizacion'),
    path('cotizaciones/cancelar/', views.cancelar_cotizacion, name='cancelar_cotizacion'),
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'),
    path('tablero/', views.tablero, name='tablero'),
    path('crear_rol/', views.crear_rol, name='crear_rol'),
    path('dashboard_analista/', views.dash_analista, name='dash_analista'),
    path('visitas/', views.listar_visitas_programadas, name='listar_visitas_programadas'),
    path('evaluar_cotizacion/<int:id_cotizacion>/', views.evaluar_cotizacion, name='evaluar_cotizacion'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('cotizaciones/recibo/<int:id_cotizacion>/', views.recibo_cotizacion, name='recibo_cotizacion'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


