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
    'groups': 'bi bi-people-fill',
    'users': 'bi bi-person-fill',
}


global PALETTE_SETTINGS

try:
    PALETTE_SETTINGS:dict = settings.PALETTE_ADMIN_SETTINGS
except Exception as e:
    PALETTE_SETTINGS = dict()

SETTINGS = {
  'site_header': 'Dj Palette',
  'site_title': 'Dj Palette',
  'site_icon': 'bi bi-palette',
  'index_title': 'Dashboard',
  'custom_urls': [],
  'custom_links': [
        {
            'label': "Support",
            'url': 'admin:support_chat', # a name from a valid url pattern,
            'left_icon': 'bi bi-support-chat', # or right_icon for positioning of the icon
        }
    ]
}

SETTINGS.update({
    'app_icons': {**BASE_APP_ICONS, **PALETTE_SETTINGS.get('app_icons', dict())},
    'model_icons': {**BASE_MODEL_ICONS, **PALETTE_SETTINGS.get('model_icons', dict())},
})



def get_base_app_icon(app_label):
    _settings = SETTINGS
    return SETTINGS['app_icons'][app_label]

def get_base_model_icon(model_name, app_label=None):
    _settings = SETTINGS
    return SETTINGS['model_icons'].get(model_name, '')


