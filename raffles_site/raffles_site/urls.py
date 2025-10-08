
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Handlers personalizados para errores
from raffles_app import views

urlpatterns = [
    # Panel de administración
    path("admin/", admin.site.urls),

    # Rutas principales de la aplicación de rifas
    path("", include("raffles_app.urls")),
]

# Servir archivos estáticos y de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Manejo de errores personalizados
# handler404 = "raffles_app.views.error_404_view"
# handler500 = "raffles_app.views.error_500_view"
