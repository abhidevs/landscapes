from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("secretpath372/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Landscapes Admin"
admin.site.site_title = "Landscapes Admin Dashboard"
admin.site.index_title = "Welcome to the Landscapes Admin Dashboard"
