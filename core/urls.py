from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import index  # Your home page view

urlpatterns = [
    path('admin/', admin.site.urls),

    # INDEX PAGE
    path('', index, name='index'),

    # APPS
    path('donor/', include('donor.urls')),           # Donor app
    path('hospital/', include('hospital.urls')),     # Hospital app
    path('request/', include('requests_app.urls')),  # Blood request app
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
