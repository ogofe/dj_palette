from django import template

register = template.Library()


@register.filter
def app_icon_class(app, icon=''):
    from dj_palette.palette_admin.conf import get_base_app_icon
    label = app['app_label']
    if label:
        return get_base_app_icon(label)
    return icon or 'bi bi-grid'


@register.filter
def model_icon_class(model, app_label=''):
    from dj_palette.palette_admin.conf import get_base_model_icon
    model_name = model.get('model_name') or model.get('object_name', '').lower()
    if model_name:
        return get_base_model_icon(model_name, app_label=app_label or None)
    return 'bi bi-table'


@register.filter
def action_label(choice_label) -> str:
    label = choice_label.split(" ")[0].strip()
    return label


@register.filter('getattr')
def get_obj_attr(obj, attr):
    # print(obj.keys())
    return getattr(obj, attr, None)

