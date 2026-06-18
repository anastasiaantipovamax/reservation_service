from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# React frontend is served by Django. Keep these routes last so they do not intercept /admin/ or /api/.
urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html'), name='frontend'),
    path('<path:unused>', TemplateView.as_view(template_name='index.html'), name='frontend-fallback'),
]
