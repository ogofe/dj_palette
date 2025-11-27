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
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_not_required
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from django.views.decorators.cache import never_cache
from django.urls import NoReverseMatch, Resolver404, resolve, reverse, reverse_lazy
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .conf import (
    SETTINGS,
)



PALETTE_SETTINGS = getattr(settings, 'PALETTE_ADMIN_SETTINGS', SETTINGS)




class PaletteAdminSite(AdminSite):
    # make the following variables dynamic from settings, e.g

    site_header = PALETTE_SETTINGS.get('site_header', "Palette Admin")
    site_title = PALETTE_SETTINGS.get('site_title', "Palette Admin")
    index_title = PALETTE_SETTINGS.get('index_title', "Palette Admin")

    def get_urls(self):
        custom_urls = [
            path('login/', self.login, name='login'),
            path('logout/', self.logout, name='logout'),
            path('password_change/', self.password_change, name='password_change'),
            path('password_change/done/', self.password_change_done, name='password_change_done'),
            path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
            path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
            path('password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(success_url='palette_admin:password_reset_done'), name='password_reset_confirm'),
            path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
            path('support_chat/', self.admin_view(self.support_chat_view), name='support_chat'),
            path('profile/', self.admin_view(self.profile_view), name='profile'),
            re_path(r'^(?P<app_label>\w+)/$', self.admin_view(self.app_index), name='app_list'),
        ] + super().get_urls()


        if PALETTE_SETTINGS.get('show_editor', True):
            custom_urls.extend([
                path('pages/', dashboard_view, name='custom-dashboard'),
                path('pages/edit/<slug:slug>/', edit_admin_page, name='edit-admin-page'),
                path('pages/<slug:slug>/', dynamic_admin_page, name='dynamic-admin-page'),
            ])
        if PALETTE_SETTINGS.get('custom_urls'):
            other_urls = PALETTE_SETTINGS.get('custom_urls', [])
            custom_urls.extend([
                path(url_path, self.admin_view(view_func), name) for (url_path, view_func, name)  in other_urls
            ])
        return custom_urls


    def logout(self, request, **kwargs):
        logout(request)
        return redirect('palette_admin:login') # Redirect to the login page after logout

    @method_decorator(never_cache)
    @login_not_required
    def login(self, request, extra_context=None):
        """
        Display the login form for the given HttpRequest.
        """
        if request.method == "GET" and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse("palette_admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)

        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.admin.forms eventually imports User.
        from django.contrib.admin.forms import AdminAuthenticationForm
        from django.contrib.auth.views import LoginView

        context = {
            **self.each_context(request),
            "title": _("Log in"),
            "subtitle": None,
            "app_path": request.get_full_path(),
            "username": request.user.get_username(),
        }
        if (
            REDIRECT_FIELD_NAME not in request.GET
            and REDIRECT_FIELD_NAME not in request.POST
        ):
            context[REDIRECT_FIELD_NAME] = reverse("palette_admin:index", current_app=self.name)
        context.update(extra_context or {})

        defaults = {
            "extra_context": context,
            'next_page': 'palette_admin:index',
            "authentication_form": self.login_form or AdminAuthenticationForm,
            "template_name": self.login_template or "admin/login.html",
        }
        request.current_app = self.name
        return LoginView.as_view(**defaults)(request)


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

        for key, value in PALETTE_SETTINGS.items():
            if key not in context:
                context[key] = value

        if PALETTE_SETTINGS.get('available_apps'):
            context['available_apps'] =  [app for app in self.get_app_list(request) if app['app_label'] in PALETTE_SETTINGS.get('available_apps') ]
        else:
            context['available_apps'] = self.get_app_list(request)
        return context
    

    # Dashboard index view
    def index(self, request, extra_context:dict=None, **kwargs):
        context:dict = self.each_context(request)
        
        now = datetime.now().time()
        greeting = 'Morning'
        if 12 < now.hour <= 16:greeting='Afternoon'
        if now.hour > 16:greeting='Evening'

        # Get recent actions by the logged-in user (last 10)
        recent_actions = LogEntry.objects.filter(
            user=request.user
        ).select_related(
            'user', 'content_type'
        ).order_by('-action_time')[:7]

        # Build admin URLs for each log entry
        for log in recent_actions:
            print("Got Action:", log)
            if not log.is_deletion() and log.object_id:
                try:
                    app_label = log.content_type.app_label
                    model_name = log.content_type.model
                    log.admin_url = reverse(
                        f'{self.name}:{app_label}_{model_name}_change',
                        args=[log.object_id],
                        current_app=self.name
                    )
                except Exception as error:
                    log.admin_url = None
            else:
                log.admin_url = None

        context.update({
            'greeting': greeting,
            'user': request.user,
            'app_list': self.get_app_list(request),
            'recent_actions': recent_actions,
            # **extra_context if extra_context else 
        })
        
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
    



# Some other config
