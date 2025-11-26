from django import template

register = template.Library()


@register.filter
def app_icon_class(app, icon=''):
    from dj_palette.palette_admin.conf import get_base_app_icon
    label = app['app_label']
    if label:
        return get_base_app_icon(label)
    return icon


@register.filter
def model_icon_class(model, icon=''):
    from dj_palette.palette_admin.conf import get_base_model_icon

    label:str = model['name'].lower()
    if label:
        return get_base_model_icon(label)
    return icon


@register.filter
def action_label(choice_label) -> str:
    label = choice_label.split(" ")[0].strip()
    return label


@register.filter('getattr')
def get_obj_attr(obj, attr):
    # print(obj.keys())
    return getattr(obj, attr, None)

