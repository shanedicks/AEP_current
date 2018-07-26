from __future__ import absolute_import, unicode_literals
import os
from django.core.exceptions import ImproperlyConfigured
from unipath import Path
from sys import path

########## PATH CONFIGURATION

# Absolute filesystem path to config directory
CONFIG_ROOT = Path(__file__).ancestor(2)

# Absolute filesystem path to project directory
PROJECT_ROOT = CONFIG_ROOT.parent

# Project added to python path
path.append(PROJECT_ROOT)


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the {} environment variable'.format(var_name)
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_env_variable("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = get_env_variable('MAILGUN_ACCESS_KEY')
MAILGUN_SERVER_NAME = 'dccaep.org'

DEFAULT_FROM_EMAIL = 'robot@dccaep.org'

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'import_export',
    'formtools',
    'rules.apps.AutodiscoverRulesConfig'
]

LOCAL_APPS = [
    'people',
    'sections',
    'semesters',
    'assessments',
    'coaching',
    'academics'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(PROJECT_ROOT.child("templates")), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

SITE_ID = 1

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

TIME_INPUT_FORMATS = [
    '%I:%M %p',
    '%H:%M:%S',
    '%H:%M'
]

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_DIRS = [PROJECT_ROOT.child("static"), ]

STATIC_ROOT = PROJECT_ROOT.child("staticfiles")

STATIC_URL = '/static/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = PROJECT_ROOT.child("media")

MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/'

# django-crispy-forms template-pack setting
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# import_export settings
IMPORT_EXPORT_USE_TRANSACTIONS = True

# Google Classroom settings
KEYFILE_DICT = {
    "type": "service_account",
    "project_id": "maximal-ceiling-171219",
    "private_key_id": get_env_variable('GOOGLE_API_KEY_ID'),
    "private_key": get_env_variable('GOOGLE_API_KEY').encode('utf-8').decode('unicode-escape'),
    "client_email": "admin-91@maximal-ceiling-171219.iam.gserviceaccount.com",
    "client_id": "112317125717967002091",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/admin-91%40maximal-ceiling-171219.iam.gserviceaccount.com"
}

# Celery settings
CELERY_RESULT_BACKEND = 'redis://'

# WorkreadyU Settings
LCTCS_PASS = get_env_variable('LCTCS_PASS')
