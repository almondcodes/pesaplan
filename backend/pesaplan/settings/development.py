"""
Development Settings for PesaPlan
"""

from .base import *

# Override base settings for development
DEBUG = True

# Development-specific apps
# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# Development middleware
# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# Development database (can use SQLite for local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development CORS settings (more permissive)
CORS_ALLOW_ALL_ORIGINS = True

# Development email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development logging (more verbose)
LOGGING['loggers']['pesaplan']['level'] = 'DEBUG'

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Development-specific settings
ALLOWED_HOSTS = ['*']
