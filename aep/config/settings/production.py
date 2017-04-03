from .base import *

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
