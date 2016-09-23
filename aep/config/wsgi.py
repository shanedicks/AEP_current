import os
from unipath import Path
from sys import path

CONFIG_ROOT = Path(__file__).ancestor(2)
path.append(CONFIG_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
