"""Authenticates Google API client libraries (Sheets/Calendar/Drive).
Client libraries reference:
    https://developers.google.com/api-client-library/python/reference/pydoc
PyDocs for googleapiclient:
    https://google.github.io/google-api-python-client/docs/epy/googleapiclient-module.html
"""

import logging
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
def auth(keyfile_dict, name=None, scopes=None, version=None):

    credentials = None
    http = httplib2.Http()

    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            keyfile_dict,
            scopes=scopes)
    except Exception as e:
        log.exception('Error creating service acct for %s: %s', name, e.message)
        raise

    try:
        http = credentials.authorize(http)
    except Exception as e:
        log.exception('Error authorizing keyfile for %s: %s', name, e.message)
        raise

    try:
        return build(name, version, http=http, cache_discovery=False)
    except Exception as e:
        log.exception('Error acquiring %s service: %s', name, e.message)
        raise

#-------------------------------------------------------------------------------
def _google_auth(json_cred):
    """google-auth not yet supported by googleapiclient
    """

    import httplib2
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google.auth.transport.urllib3 import AuthorizedHttp

    timer = Timer()

    #http = httplib2.Http()
    scopes=['https://www.googleapis.com/auth/spreadsheets']
    name='sheets'
    version='v4'

    creds = service_account.Credentials.from_service_account_info(json_cred)
    scoped_creds = creds.with_scopes(scopes)

    log.debug('Setup credentials. Value=%s [%s]', scoped_creds.valid, timer.clock(stop=False))

    authed_http = AuthorizedHttp(scoped_creds)

    try:
        service = build('sheets', 'v4', http=authed_http) #, cache_discovery=False)
    except Exception as e:
        log.exception('Failed to acquire Sheets client.')
        raise
    else:
        log.debug('Acquired Sheets client. [%s]', timer.clock(stop=False))

        return service
