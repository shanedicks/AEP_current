from .base import *

########## CELERY CONFIGURATION
CELERY_BROKER_URL = get_env_variable('CLOUDAMQP_URL')
CELERY_BROKER_POOL_LIMIT = 1
########## END CELERY CONFIGURATION

########## DATABASE CONFIGURATION
import dj_database_url
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=500)
########## END DATABASE CONFIGURATION

ALLOWED_HOSTS = [
    'dccaep.herokuapp.com',
    'www.dccaep.org',
    'dccaep.org',
    'dccaeptest.herokuapp.com'
]

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
