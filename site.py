from django.contrib.admin import AdminSite
from django.urls import path
from .views import dashboard_view, dynamic_admin_page, edit_admin_page

PALETTE_SETTINGS = {
  'site_header': 'Daily Post',
  'index_title': 'Dashboard',
  'custom_urls': [],
  'custom_links': [
        {
            'label': "Support",
            'url_name': 'admin:support_chat', # a name from a valid url pattern,
            'left_icon': 'bi bi-support-chat', # or right_icon for positioning of the icon
        }
    ],

}




class PaletteAdminSite(AdminSite):
    # make the following variables dynamic from settings, e.g

    site_header = PALETTE_SETTINGS.get('site_header', "Palette Admin")
    site_title = PALETTE_SETTINGS.get('site_title', "Palette Admin")
    index_title = PALETTE_SETTINGS.get('index_title', "Palette Admin")

    def get_urls(self):
        urls = super().get_urls()

        if PALETTE_SETTINGS.get('show_editor', True):
            custom_urls = [
                path('dashboard/', dashboard_view, name='custom-dashboard'),
                path('edit/<slug:slug>/', edit_admin_page, name='edit-admin-page'),
                path('<slug:slug>/', dynamic_admin_page, name='dynamic-admin-page'),
            ]
            urls.extend(custom_urls)
        if PALETTE_SETTINGS.get('custom_urls'):
            custom_urls = PALETTE_SETTINGS.get('custom_urls', [])
            urls.extend(custom_urls)
        return urls

    def each_context(self, request):
        context = super().each_context(request)
        context['custom_links'] = PALETTE_SETTINGS.get('custom_links', [])
        return context

