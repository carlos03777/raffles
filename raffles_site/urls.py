
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve

# Handlers personalizados para errores
from raffles_app import views

urlpatterns = [
    # Panel de administración
    path("admin/", admin.site.urls),

    # Rutas principales de la aplicación de rifas
    path("", include("raffles_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# En producción (S3) Django no sirve los archivos, el bucket lo hace


# Manejo de errores personalizados
handler404 = "raffles_app.views.error_404_view"
handler500 = "raffles_app.views.error_500_view"