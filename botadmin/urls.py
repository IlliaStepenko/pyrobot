from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from botadmin import settings

urlpatterns = [
    path('admin/', admin.site.urls),
]
