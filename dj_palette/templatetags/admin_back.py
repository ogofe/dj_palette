from django import template
from django.urls import reverse
import re

register = template.Library()

@register.simple_tag(takes_context=True)
def admin_back_url(context):
    path = context['request'].path
    # Matches /admin/app/model/add/
    m = re.match(r'^/admin/([^/]+)/([^/]+)/add/$', path)
    if m:
        app, model = m.groups()
        return f"/admin/{app}/{model}/"
    # Matches /admin/app/model/pk/change/
    m = re.match(r'^/admin/([^/]+)/([^/]+)/\d+/change/$', path)
    if m:
        app, model = m.groups()
        return f"/admin/{app}/{model}/"
    # Matches /admin/app/model/
    m = re.match(r'^/admin/([^/]+)/([^/]+)/$', path)
    if m:
        app = m.group(1)
        return f"/admin/{app}/"
    # Default: admin index
    return reverse('admin:index')

