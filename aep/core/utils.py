import csv
import datetime
import logging
import os
import requests
from apiclient import discovery
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.apps import apps
from django.core.mail.message import EmailMessage
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger(__name__)

CHAR_MAP = {
    '\xc0': 'A',
    '\xc1': 'A',
    '\xc2': 'A',
    '\xc3': 'A',
    '\xc4': 'A',
    '\xc5': 'A',
    '\xe0': 'a',
    '\xe1': 'a',
    '\xe2': 'a',
    '\xe3': 'a',
    '\xe4': 'a',
    '\xe5': 'a',
    '\xc7': 'C',
    '\xe7': 'c',
    '\xd0': 'D',
    '\xf0': 'd',
    '\xc8': 'E',
    '\xc9': 'E',
    '\xca': 'E',
    '\xcb': 'E',
    '\xe8': 'e',
    '\xe9': 'e',
    '\xea': 'e',
    '\xeb': 'e',
    '\xcc': 'I',
    '\xcd': 'I',
    '\xce': 'I',
    '\xcf': 'I',
    '\xec': 'i',
    '\xed': 'i',
    '\xee': 'i',
    '\xef': 'i',
    '\xd1': 'N',
    '\xf1': 'n',
    '\xd2': 'O',
    '\xd3': 'O',
    '\xd4': 'O',
    '\xd5': 'O',
    '\xd6': 'O',
    '\xd8': 'O',
    '\xf2': 'o',
    '\xf3': 'o',
    '\xf4': 'o',
    '\xf5': 'o',
    '\xf6': 'o',
    '\xf8': 'o',
    '\xd9': 'U',
    '\xda': 'U',
    '\xdb': 'U',
    '\xdc': 'U',
    '\xf9': 'u',
    '\xfa': 'u',
    '\xfb': 'u',
    '\xfc': 'u',
    '\xdd': 'Y',
    '\xfd': 'y',
    '\xff': 'y',
    '\xc6': 'Ae',
    '\xe6': 'ae',
    '\xde': 'Th',
    '\xfe': 'th',
    '\xdf': 'ss',
    '\u0100': 'A',
    '\u0102': 'A',
    '\u0104': 'A',
    '\u0101': 'a',
    '\u0103': 'a',
    '\u0105': 'a',
    '\u0106': 'C',
    '\u0108': 'C',
    '\u010a': 'C',
    '\u010c': 'C',
    '\u0107': 'c',
    '\u0109': 'c',
    '\u010b': 'c',
    '\u010d': 'c',
    '\u010e': 'D',
    '\u0110': 'D',
    '\u010f': 'd',
    '\u0111': 'd',
    '\u0112': 'E',
    '\u0114': 'E',
    '\u0116': 'E',
    '\u0118': 'E',
    '\u011a': 'E',
    '\u0113': 'e',
    '\u0115': 'e',
    '\u0117': 'e',
    '\u0119': 'e',
    '\u011b': 'e',
    '\u011c': 'G',
    '\u011e': 'G',
    '\u0120': 'G',
    '\u0122': 'G',
    '\u011d': 'g',
    '\u011f': 'g',
    '\u0121': 'g',
    '\u0123': 'g',
    '\u0124': 'H',
    '\u0126': 'H',
    '\u0125': 'h',
    '\u0127': 'h',
    '\u0128': 'I',
    '\u012a': 'I',
    '\u012c': 'I',
    '\u012e': 'I',
    '\u0130': 'I',
    '\u0129': 'i',
    '\u012b': 'i',
    '\u012d': 'i',
    '\u012f': 'i',
    '\u0131': 'i',
    '\u0134': 'J',
    '\u0135': 'j',
    '\u0136': 'K',
    '\u0137': 'k',
    '\u0138': 'k',
    '\u0139': 'L',
    '\u013b': 'L',
    '\u013d': 'L',
    '\u013f': 'L',
    '\u0141': 'L',
    '\u013a': 'l',
    '\u013c': 'l',
    '\u013e': 'l',
    '\u0140': 'l',
    '\u0142': 'l',
    '\u0143': 'N',
    '\u0145': 'N',
    '\u0147': 'N',
    '\u014a': 'N',
    '\u0144': 'n',
    '\u0146': 'n',
    '\u0148': 'n',
    '\u014b': 'n',
    '\u014c': 'O',
    '\u014e': 'O',
    '\u0150': 'O',
    '\u014d': 'o',
    '\u014f': 'o',
    '\u0151': 'o',
    '\u0154': 'R',
    '\u0156': 'R',
    '\u0158': 'R',
    '\u0155': 'r',
    '\u0157': 'r',
    '\u0159': 'r',
    '\u015a': 'S',
    '\u015c': 'S',
    '\u015e': 'S',
    '\u0160': 'S',
    '\u015b': 's',
    '\u015d': 's',
    '\u015f': 's',
    '\u0161': 's',
    '\u0162': 'T',
    '\u0164': 'T',
    '\u0166': 'T',
    '\u0163': 't',
    '\u0165': 't',
    '\u0167': 't',
    '\u0168': 'U',
    '\u016a': 'U',
    '\u016c': 'U',
    '\u016e': 'U',
    '\u0170': 'U',
    '\u0172': 'U',
    '\u0169': 'u',
    '\u016b': 'u',
    '\u016d': 'u',
    '\u016f': 'u',
    '\u0171': 'u',
    '\u0173': 'u',
    '\u0174': 'W',
    '\u0175': 'w',
    '\u0176': 'Y',
    '\u0177': 'y',
    '\u0178': 'Y',
    '\u0179': 'Z',
    '\u017b': 'Z',
    '\u017d': 'Z',
    '\u017a': 'z',
    '\u017c': 'z',
    '\u017e': 'z',
    '\u0132': 'IJ',
    '\u0133': 'ij',
    '\u0152': 'Oe',
    '\u0153': 'oe',
    '\u0149': "'n",
    '\u017f': 's',
    '.': '',
    ',': '',
    "'": '',
    '\u2018': '',
    '\u2019': '',
}

def make_AEP_ID():
    return get_random_string(length=8, allowed_chars='0123456789')

def make_slug():
    return get_random_string(length=5)

def plivo_num(phone):
    return "1{0}".format(phone)

def make_unique_slug(app, model):
    model_class = apps.get_model(app, model)
    duplicate = True
    while duplicate:
        slug = get_random_string(length=5)
        if model_class.objects.filter(slug=slug).exists():
            continue
        else:
            duplicate = False
    return slug


def render_to_csv(data, filename):
    response = HttpResponse(content_type="text/csv")
    cd = 'attachment; filename="{0}"'.format(filename)
    response['Content-Disposition'] = cd
    data = data

    writer = csv.writer(response)
    for row in data:
        writer.writerow(row)
    return response

def custom_report(data, filename, email_address):
    with open(filename, 'w', newline='') as out:
        writer = csv.writer(out)
        for row in data:
            writer.writerow(row)

    email = EmailMessage(
        'Custom report',
        'This is a custom data report',
        'reporter@dccaep.org',
        [email_address]
    )
    email.attach_file(filename)
    email.send()
    os.remove(filename)

def get_fiscal_year_start_date():
    today = timezone.now()
    if today.month >= 7:
        year = today.year
    else:
        year = today.year - 1
    return datetime.date(year, 7, 1)

def get_fiscal_year_end_date():
    today = timezone.now()
    if today.month >= 7:
        year = today.year +1
    else:
        year = today.year
    return datetime.date(year, 6, 30)

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

def directory_service():
    scopes = [
        'https://www.googleapis.com/auth/admin.directory.user',
    ]

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    gb = credentials.create_delegated('greenbean@elearnclass.org')
    http_auth = gb.authorize(Http())
    return discovery.build('admin', 'directory_v1', http=http_auth)

def drive_service():
    scopes = [
        'https://www.googleapis.com/auth/drive.file',
    ]

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    gb = credentials.create_delegated('greenbean@elearnclass.org')
    http_auth = gb.authorize(Http())
    return discovery.build('drive', 'v3', http=http_auth)

def classroom_service():

    scopes = [
        'https://www.googleapis.com/auth/classroom.courses',
        'https://www.googleapis.com/auth/classroom.rosters'
    ]

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    shane = credentials.create_delegated('greenbean@elearnclass.org')
    http_auth = shane.authorize(Http())
    return discovery.build('classroom', 'v1', http=http_auth)

def clean_special_characters(input_string):
    cleaned_chars = [CHAR_MAP[c] if c in CHAR_MAP else c for c in input_string]
    return "".join(cleaned_chars)


def time_string_to_hours(time_str, source):
    if source == "Essential Ed":
        hours, minutes, seconds = map(int, time_str.split(':'))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        hours_float = total_seconds / 3600.0
    if source == "Duolingo":
        hours, minutes = map(int, [part.strip('hm') for part in time_str.split()])
        hours_float = hours + minutes / 60.0
    return round(hours_float,2)


class DriveUploadError(ValidationError):
    pass

def file_to_drive(name, file, folder_id):
    try: 
        service = drive_service()
        metadata = {
            'name': name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(
            file.temporary_file_path(),
            mimetype=file.content_type,
        )
        file = service.files().create(
            body=metadata,
            media_body=media,
            fields='id'
        ).execute()
    except HttpError as e:
        logger.info(f"DriveUploadError: {str(e)}")
        raise DriveUploadError(f"Failed to upload file: {str(e)}")
    return file.get('id')
