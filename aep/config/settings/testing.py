import os
import tempfile

from .base import *

# DEBUG must be False: config/urls.py appends the 400/403/404/500 debug routes
# when it is True, which would make the URL smoke sweep differ between settings
# modules.
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'aep'),
        'USER': os.environ.get('DATABASE_USER', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', ''),
        'PORT': os.environ.get('DATABASE_PORT', ''),
    }
}

# Collect mail in memory instead of handing it to Mailgun. This is what makes
# the EmailMessage(...).send() calls in the report tasks assertable.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Tasks are neutered by an autouse fixture in tests/conftest.py. The memory
# broker is a seatbelt: a .delay that slips past the patch fails immediately
# instead of blocking on an amqp connect timeout.
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'
    },
}

MEDIA_ROOT = tempfile.mkdtemp(prefix='gb-test-media-')

# No STATIC_ROOT in tests, so WhiteNoise only logs noise.
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m]

# Dummy credentials. Deliberately invalid: if a mock ever fails to cover a seam,
# the call should fail against a bogus credential rather than succeed against
# production Google Workspace / Plivo / WorkReadyU.
ANYMAIL = {'MAILGUN_API_KEY': 'test-not-a-real-key'}
LCTCS_PASS = 'test-not-a-real-password'
PLIVO_AUTH_ID = 'test-not-a-real-id'
PLIVO_AUTH_TOKEN = 'test-not-a-real-token'
PROXIE_DICT = {'http': '', 'https': ''}
KEYFILE_DICT = {
    **KEYFILE_DICT,
    'private_key_id': 'test-not-a-real-key-id',
    'private_key': 'test-not-a-real-private-key',
}
