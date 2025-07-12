from django.contrib import admin
from .site import PaletteAdminSite
from .models import AdminPage, Component
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

# admin.site.register(AdminPage)
# admin.site.register(Component)

palette_admin = PaletteAdminSite(name='palette_admin')
palette_admin.register(AdminPage)
palette_admin.register(Component)
palette_admin.register(User)
palette_admin.register(Group)
