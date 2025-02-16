
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Apps.Aplicacion1.urls')),  # Incluir las rutas de tu aplicación

]

# Solo sirve archivos de medios si DEBUG es True (modo de desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)