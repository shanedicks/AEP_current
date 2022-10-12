from .base import *

# Celery Configuration
CELERY_BROKER_URL = get_env_variable('CLOUDAMQP_URL')
celery_url = get_env_variable('REDIS_URL')
parameters = "/?ssl_cert_required=required"
CELERY_RESULT_BACKEND = celery_url+parameters

# Database Configuration
import dj_database_url
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=500)

ALLOWED_HOSTS = [
    'dccaep.herokuapp.com',
    'www.dccaep.org',
    'dccaep.org',
    'dccaeptest.herokuapp.com'
]

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
