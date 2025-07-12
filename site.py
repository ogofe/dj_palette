from django.contrib.admin import AdminSite
from django.urls import path, re_path
from .views import dashboard_view, dynamic_admin_page, edit_admin_page
from django.template.response import TemplateResponse
from django.contrib.auth import logout, login
from django.shortcuts import redirect
from datetime import datetime
from django.apps import apps
from django.http import Http404
from django.utils.module_loading import import_string


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
    # login_template = 'admin/login.html'
    # logout_template = 'admin/logout.html'

    def get_urls(self):
        custom_urls = [
            path('login/', self.login, name='login'),
            path('logout/', self.logout, name='logout'),
            path('password_change/', self.password_change, name='password_change'),
            path('password_change/done/', self.password_change_done, name='password_change_done'),
            # path('password_reset/', self.password_reset, name='password_reset'),
            # path('password_reset/done/', self.password_reset_done, name='password_reset_done'),
            # path('reset/<uidb64>/<token>/', self.password_reset_confirm, name='password_reset_confirm'),
            # path('reset/done/', self.password_reset_complete, name='password_reset_complete'),
            path('support_chat/', self.admin_view(self.support_chat_view), name='support_chat'),
            path('profile/', self.admin_view(self.profile_view), name='user-profile'),
            re_path(r'^(?P<app_label>\w+)/$', self.admin_view(self.app_index), name='app_list'),
        ]

        if PALETTE_SETTINGS.get('show_editor', True):
            custom_urls.extend([
                path('pages/', dashboard_view, name='custom-dashboard'),
                path('pages/edit/<slug:slug>/', edit_admin_page, name='edit-admin-page'),
                path('pages/<slug:slug>/', dynamic_admin_page, name='dynamic-admin-page'),
            ])
        if PALETTE_SETTINGS.get('custom_urls'):
            other_urls = PALETTE_SETTINGS.get('custom_urls', [])
            custom_urls.extend(other_urls)
        return custom_urls + super().get_urls()

    def logout(self, request, **kwargs):
        logout(request)
        return redirect('admin:login') # Redirect to the login page after logout

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)

        # Inject model manager as model.objects for template use
        for app_label, app in app_dict.items():
            for model_dict in app['models']:
                model_class = self._registry[model_dict['model']].model
                model_dict['objects'] = model_class._default_manager  # or .objects

        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        return app_list


    def each_context(self, request):
        context = super().each_context(request)
        context['custom_links'] = PALETTE_SETTINGS.get('custom_links', [])
        return context
    
    # Dashboard index view
    def index(self, request, extra_context=None, **kwargs):
        context = self.each_context(request)
        
        now = datetime.now().time()
        greeting = 'Morning'
        if 12 < now.hour <= 16:greeting='Afternoon'
        if now.hour > 16:greeting='Evening'

        context['greeting'] = greeting
        context['user'] = request.user
        return TemplateResponse(request, "admin/index.html", context)

    def app_index(self, request, app_label, extra_context=None):
        app_config = apps.get_app_config(app_label)
        if not app_config:
            raise Http404("App not found")

        context = {
            **self.each_context(request),
            "title": app_config.verbose_name,
            "app_label": app_label,
            "app_list": [app for app in self.get_app_list(request) if app['app_label'] == app_label],
        }
        print("App List:", context['app_list'])
        context.update(extra_context or {})
        return TemplateResponse(request, "admin/app_index.html", context)


    def profile_view(self, request):
        """
        Custom view to handle profile viewing.
        """
        context = self.each_context(request)
        context['title'] = "User Profile"
        context['user'] = request.user
        return TemplateResponse(request, "admin/profile.html", context)

    def support_chat_view(self, request):
        """
        Custom view to handle profile viewing.
        """
        context = self.each_context(request)
        context['title'] = "User Profile"
        context['user'] = request.user
        return TemplateResponse(request, "admin/profile.html", context)
    
