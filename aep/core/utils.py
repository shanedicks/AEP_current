import csv
import datetime
import logging
import os
import requests
from time import sleep
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

def get_inactive_users(
    service,
    inactive_threshold_days: int = 365,
    created_threshold_days: int = 90
):

    inactive_users = []
    now = timezone.now()
    inactive_threshold = now - datetime.timedelta(days=inactive_threshold_days)
    creation_threshold = now - datetime.timedelta(days=created_threshold_days)

    try:
        request = service.users().list(
            domain='elearnclass.org',
            orderBy='email',
            projection='basic',
            fields='nextPageToken,users(primaryEmail,creationTime,lastLoginTime)',
            maxResults=500
        )

        page_count = 0
        total_users = 0
        while request is not None:
            response = request.execute()
            users = response.get('users', [])
            page_count += 1
            total_users += len(users)
            logger.info(f"Processing page {page_count}, found {len(users)} users on this page, total so far: {total_users}")

            for user in users:
                creation_time = timezone.datetime.fromisoformat(
                    user['creationTime'].replace('Z', '+00:00')
                )

                last_login_time = timezone.datetime.fromisoformat(
                    user['lastLoginTime'].replace('Z', '+00:00')
                )

                if last_login_time < inactive_threshold and creation_time < creation_threshold:
                    inactive_users.append(user)

            request = service.users().list_next(request, response)

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise

    return inactive_users

def delete_inactive_users(
    service,
    email_address: str,
    inactive_threshold_days: int = 365,
    created_threshold_days: int = 90
):
    results = {
        'total_inactive': 0,
        'deleted': 0,
        'errors': 0,
        'error_details': []
    }
    
    deletion_records = [['Email', 'Creation Time', 'Last Login', 'Status']]
    successfully_deleted = []

    try:
        inactive_users = get_inactive_users(service, inactive_threshold_days, created_threshold_days)
        results['total_inactive'] = len(inactive_users)

        for i, user in enumerate(inactive_users):
            try:
                service.users().delete(userKey=user['primaryEmail']).execute()
                results['deleted'] += 1
                logger.info(f"Deleted user: {user['primaryEmail']}")

                successfully_deleted.append(user['primaryEmail'])
                deletion_records.append([
                    user['primaryEmail'],
                    user['creationTime'],
                    user.get('lastLoginTime', 'Never'),
                    'Deleted Successfully'
                ])

                sleep(0.06)

                if i > 0 and i % 1000 == 0:
                    logger.info(f"Processed {i} deletions, pausing before next batch...")
                    sleep(60)

            except Exception as e:
                results['errors'] += 1
                error_detail = {
                    'email': user['primaryEmail'],
                    'error': str(e)
                }
                results['error_details'].append(error_detail)
                logger.error(f"Error deleting user {user['primaryEmail']}: {str(e)}")

                deletion_records.append([
                    user['primaryEmail'],
                    user['creationTime'],
                    user.get('lastLoginTime', 'Never'),
                    f'Error: {str(e)}'
                ])

        if successfully_deleted:
            ElearnRecord = apps.get_model('coaching', 'ElearnRecord')
            updated = ElearnRecord.objects.filter(
                g_suite_email__in=successfully_deleted
            ).update(g_suite_email='')
            results['records_cleared'] = updated
            logger.info(f"Cleared {updated} ElearnRecord g_suite_email fields")

        filename = f'user_deletion_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        custom_report(deletion_records, filename, email_address)

    except Exception as e:
        logger.error(f"Error in delete_inactive_users: {str(e)}")
        raise

    return results

def get_courses_and_teachers():
    service = classroom_service()
    courses_result = service.courses().list().execute()
    courses = courses_result.get('courses', [])

    course_details = []
    for course in courses:
        course_id = course['id']
        course_name = course['name']
        owner_id = course.get('ownerId', 'N/A')

        teachers_result = service.courses().teachers().list(courseId=course_id).execute()
        teachers = teachers_result.get('teachers', [])

        teacher_details = []
        for teacher in teachers:
            email = teacher.get('userId', 'N/A')
            profile = teacher.get('profile', {})
            name = profile.get('name', {}).get('fullName', email)

            teacher_details.append({
                'email': email,
                'name': name,
                'role': 'Owner' if email == owner_id else 'Teacher'
            })

        course_details.append({
            'course_id': course_id,
            'name': course_name,
            'section': course.get('section', 'N/A'),
            'owner_id': owner_id,
            'teachers': teacher_details
        })

    return course_details
