from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
import sys
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings


scopes = ['https://www.googleapis.com/auth/admin.directory.user']

lookup = sys.argv[1]

def main(lookup):

    credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
        keyfile_dict=settings.KEYFILE_DICT,
        scopes=scopes
    )

    shane = credentials.create_delegated('shane.dicks@elearnclass.org')
    http_auth = shane.authorize(Http())
    service = discovery.build('admin', 'directory_v1', http=http_auth)

    x = 0
    def check_email(name, x): # check g_suite for email, add numbers incrementally if email in use until email is valid
        if x == 0:
            email = "@".join([name, 'elearnclass.org'])
            try:
                user = service.users().get(userKey=email).execute()
                return check_email(name, x + 1)
            except:
                print(email)
        else:
            new_name = "{0}{1}".format(name, x)
            new_email = "@".join([new_name, 'elearnclass.org'])
            try:
                user = service.users().get(userKey=new_email).execute()
                return check_email(name, x + 1)
            except:
                print(new_email)

    check_email(lookup, x)

    try:
        user = service.users().get(userKey=lookup).execute()
        print('True')
    except:
        print('False')

if __name__ == '__main__':
    main(lookup)
