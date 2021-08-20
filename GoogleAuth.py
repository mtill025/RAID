from __future__ import print_function
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleAuth:

    def __init__(self, scopes):
        self.scopes = scopes
        self.credentials = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.credentials = Credentials.from_authorized_user_file('token.json', scopes)
        self.refresh_creds()

    def initialize_oauth(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', self.scopes)
        credentials = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    def refresh_creds(self):
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
