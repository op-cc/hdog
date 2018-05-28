from .base import *

AUTH_PASSWORD_VALIDATORS = []

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()
