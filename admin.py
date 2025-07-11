from django.contrib import admin
from .site import PaletteAdminSite
from .models import AdminPage, Component


# admin.site.register(AdminPage)
# admin.site.register(Component)

palette_admin = PaletteAdminSite(name='palette_admin')
palette_admin.register(AdminPage)
palette_admin.register(Component)
