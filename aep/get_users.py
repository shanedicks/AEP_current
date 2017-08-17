from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings


scopes = ['https://www.googleapis.com/auth/admin.directory.user']


def main():

    print(settings.KEYFILE_DICT['private_key'])

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    shane = credentials.create_delegated('shane.dicks@elearnclass.org')
    http_auth = shane.authorize(Http())
    service = discovery.build('admin', 'directory_v1', http=http_auth)

    print("Contacting Google")
    print("...")
    print("...")
    print('Getting the first 500 users in the domain')
    results = service.users().list(domain='elearnclass.org', maxResults=500).execute()
    users = results.get('users', [])

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print('{0} ({1})'.format(
                user['primaryEmail'],
                user['name']['fullName']
            )
            )

if __name__ == '__main__':
    main()
