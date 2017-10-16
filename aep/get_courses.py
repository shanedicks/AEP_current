from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings


scopes = ['https://www.googleapis.com/auth/classroom.courses']


def main():

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    acct = credentials.create_delegated('shane.dicks@elearnclass.org')
    http_auth = acct.authorize(Http())
    service = discovery.build('classroom', 'v1', http=http_auth)

    print("Contacting Google")
    print("...")
    print("...")
    print('Retrieving Courses')
    results = service.courses().list().execute()
    courses = results.get('courses', [])

    if not courses:
        print('No Courses in the domain.')
    else:
        print('Courses:')
        for course in courses:
            print('{0} ({1})'.format(
                course['name'],
                course.get('section', '')
            )
            )

if __name__ == '__main__':
    main()
