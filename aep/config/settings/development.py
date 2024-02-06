from .base import *

DEBUG = True

# Override the logging configuration for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['console']['formatter'] = 'verbose'
LOGGING['formatters']['verbose'] = {
    'format': '{levelname} {asctime} {module} {message}',
    'style': '{',
    'datefmt': '%Y-%m-%d %H:%M:%S',
}
LOGGING['loggers']['']['level'] = 'DEBUG'

ALLOWED_HOSTS = [
    '127.0.0.1',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('DATABASE_NAME'),
        'USER': get_env_variable('DATABASE_USER'),
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': '',
        'PORT': '',
    }
}
