from __future__ import print_function
from raid import RaidAsset, RaidResponse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path


class GoogleAuth:

    def __init__(self, scopes):
        # Scopes set the access permissions
        self.scopes = scopes
        self.credentials = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('secrets/token.json'):
            self.credentials = Credentials.from_authorized_user_file('secrets/token.json', scopes)
        self.refresh_creds()

    def initialize_oauth(self):
        """Opens browser window and asks user to sign in to Google. Builds OAuth window using information
        in credentials.json"""
        flow = InstalledAppFlow.from_client_secrets_file(
            'secrets/credentials.json', self.scopes)
        credentials = flow.run_local_server(port=0)
        with open('secrets/token.json', 'w') as token:
            token.write(credentials.to_json())

    def refresh_creds(self):
        """Attempts to use the refresh token to refresh OAuth access"""
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())


class GoogleController:

    class GoogleAsset(RaidAsset):
        def __init__(self, assetinfo):
            super().__init__(assetinfo)

    def __init__(self):
        """Wrapper for interacting with the Google Admin API."""
        scopes = ['https://www.googleapis.com/auth/admin.directory.device.chromeos',
                  'https://www.googleapis.com/auth/admin.directory.orgunit']
        self.google_auth = GoogleAuth(scopes)
        if not self.google_auth.credentials:
            self.google_auth.initialize_oauth()
        self.service = build('admin', 'directory_v1', credentials=self.google_auth.credentials)

    def search(self, serial):
        """Searches AirWatch for serial number. Returns RaidAsset object. """
        results = self.service.chromeosdevices().list(customerId="my_customer", query=serial,
                                                      projection="BASIC").execute()
        matches = len(results['chromeosdevices'])
        if matches == 1:
            return self.GoogleAsset(results['chromeosdevices'][0])
        elif matches > 1:
            return self.GoogleAsset(RaidResponse('g301').json)
        return self.GoogleAsset(RaidResponse('g302').json)

    def update_asset(self, attr, serial, new_data):
        result = self.get_device_id(serial)
        payload = {
            attr: new_data
        }
        if result:
            response = self.service.chromeosdevices().update(customerId="my_customer",
                                                             deviceId=result,
                                                             body=payload,
                                                             projection="BASIC").execute()
            return self.GoogleAsset(response)
        return self.GoogleAsset(RaidResponse('g400').json)

    def update_asset_name(self, serial, new_name):
        return self.update_asset("annotatedAssetId", serial, new_name)

    def update_asset_tag(self, serial, new_tag):
        return self.update_asset("notes", serial, new_tag)

    def update_asset_org(self, serial, new_org):
        result = self.get_device_id(serial)
        if result:
            payload = {
                'deviceIds': [
                    result
                ]
            }
            response = self.service.chromeosdevices().moveDevicesToOu(customerId="my_customer",
                                                                      orgUnitPath=new_org,
                                                                      body=payload).execute()
            return self.GoogleAsset(response)
        return self.GoogleAsset(RaidResponse('g401').json)

    def get_device_id(self, serial):
        result = self.search(serial)
        if result.raid_code['code'] == 'r200':
            return result.deviceId
        return None
