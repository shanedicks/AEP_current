import csv
import datetime
import requests
from apiclient import discovery
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.utils.crypto import get_random_string
from django.utils import timezone
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

def get_fiscal_year_start_date():
    today = timezone.now()
    if today.month >= 7:
        year = today.year
    else:
        year = today.year - 1
    return timezone.make_aware(datetime.date(year, 7, 1))


def state_session():
    session = requests.Session()

    login = {
        'Provider': '9',
        'Parish': '19',
        'Login': 'greenbean',
        'Password': settings.LCTCS_PASS,
        'btnLogin': 'Sign In'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
    }

    session.post('https://workreadyu.lctcs.edu/UserProfile/Login', data=login, headers=headers, proxies=settings.PROXIE_DICT)

    return session

def g_suite_service():
    scopes = ['https://www.googleapis.com/auth/admin.directory.user']

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    shane = credentials.create_delegated('shane.dicks@elearnclass.org')
    http_auth = shane.authorize(Http())
    return discovery.build('admin', 'directory_v1', http=http_auth)
