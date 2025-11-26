from django.contrib import admin
from django.urls import path
from dj_palette.palette_admin.admin import palette_admin

urlpatterns = [
    path('admin/', palette_admin.urls),
    path('old-admin/', admin.site.urls),
]
