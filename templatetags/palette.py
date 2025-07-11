from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.filter(name='custom_admin_render')
def custom_admin_render(component_name, props_str=""):
    props_dict = {}
    try:
        for item in props_str.split(";"):
            if item.strip():
                key, val = item.split(":", 1)
                props_dict[key.strip()] = val.strip()
    except Exception as e:
        props_dict["error"] = str(e)
    return render_to_string(f"custom_admin/components/{component_name}.html", {"props": props_dict})
