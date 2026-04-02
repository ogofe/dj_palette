from django.conf import settings


BASE_APP_ICONS = {
    'auth': 'bi bi-person-badge',
    'api': 'bi bi-bezier', # for any app named api
    'blog': 'bi bi-journal-richtext', # for any app named blog
    'shop': 'bi bi-shop', # for any app named shop
    'store': 'bi bi-shop', # for any app named store
    'core': 'bi bi-cpu', # for any app named core
    'contacts': 'bi bi-person-lines-fill', # for any app named contacts
    'accounts': 'bi bi-person-rolodex', # for any app named accounts
    'inventory': 'bi bi-clipboard2', # for any app named inventory
    'chat': 'bi bi-chat-text', # for any app named inventory
    'messages': 'bi bi-chat-right-text', # for any app named inventory
}


BASE_MODEL_ICONS = {
    'group': 'bi bi-people-fill',
    'user': 'bi bi-person-fill',
}


global PALETTE_ADMIN_SETTINGS

try:
    PALETTE_ADMIN_SETTINGS:dict = settings.PALETTE_ADMIN_SETTINGS
except Exception as e:
    PALETTE_ADMIN_SETTINGS = dict()

SETTINGS = {
  'site_header': 'Dj Palette',
  'site_title': 'Dj Palette',
  'site_icon': 'bi bi-palette',
  'index_title': 'Dashboard',
  'custom_urls': [],
  'custom_links': []
}

SETTINGS.update({
    'app_icons': {**BASE_APP_ICONS, **PALETTE_ADMIN_SETTINGS.get('app_icons', dict())},
    'model_icons': {**BASE_MODEL_ICONS, **PALETTE_ADMIN_SETTINGS.get('model_icons', dict())},
    'hidden_apps': PALETTE_ADMIN_SETTINGS.get('hidden_apps', []),
    'hidden_models': PALETTE_ADMIN_SETTINGS.get('hidden_models', {}),
})



def get_base_app_icon(app_label):
    return SETTINGS['app_icons'].get(app_label, 'bi bi-grid')

def get_base_model_icon(model_name, app_label=None):
    icons = SETTINGS['model_icons']
    if app_label:
        specific = f'{app_label}.{model_name}'
        if specific in icons:
            return icons[specific]
    return icons.get(model_name, 'bi bi-table')

def is_app_hidden(app_label):
    return app_label in SETTINGS.get('hidden_apps', [])

def is_model_hidden(app_label, model_name):
    hidden = SETTINGS.get('hidden_models', {})
    return model_name in hidden.get(app_label, [])


