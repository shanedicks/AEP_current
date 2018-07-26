import csv
import requests
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.conf import settings


def make_AEP_ID():
    return get_random_string(length=8, allowed_chars='0123456789')


def make_slug():
    return get_random_string(length=5)


def render_to_csv(data, filename):
    response = HttpResponse(content_type="text/csv")
    cd = 'attachment; filename="{0}"'.format(filename)
    response['Content-Disposition'] = cd
    data = data

    writer = csv.writer(response)
    for row in data:
        writer.writerow(row)

    return response

def state_session():
    session = requests.Session()

    login = {
        'Provider': '9',
        'Parish': '19',
        'Login': 'greenbean',
        'Password': settings.LCTCS_PASS,
        'btnLogin': 'Login'
    }

    session.post('https://workreadyu.lctcs.edu/UserProfile/Login', data=login)

    return session
