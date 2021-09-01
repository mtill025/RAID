from __future__ import print_function
from raid import RaidAsset, RaidResponse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path


class GoogleAuth:

    def __init__(self, scopes):
        # Scopes set the access permissions
        self.scopes = scopes
        self.credentials = None
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
            self.platform = "Google"
            if 'serialNumber' in self.dict:
                self.serial = self.serialNumber
            if 'annotatedAssetId' in self.dict:
                self.name = self.annotatedAssetId
            if 'notes' in self.dict:
                self.asset_tag = self.notes
            if 'orgUnitPath' in self.dict:
                self.org_unit = self.orgUnitPath

    def __init__(self):
        """Wrapper for interacting with the Google Admin API."""
        scopes = ['https://www.googleapis.com/auth/admin.directory.device.chromeos',
                  'https://www.googleapis.com/auth/admin.directory.orgunit']
        self.google_auth = GoogleAuth(scopes)
        if not self.google_auth.credentials:
            self.google_auth.initialize_oauth()
        self.service = build('admin', 'directory_v1', credentials=self.google_auth.credentials)
        self.platform = "Google"

    def search(self, serial, level="BASIC"):
        """Searches Google for serial number. Returns RaidAsset object. """
        results = self.service.chromeosdevices().list(customerId="my_customer", query=serial,
                                                      projection=level).execute()
        if 'chromeosdevices' not in results:
            return self.GoogleAsset(RaidResponse('302').json)
        matches = len(results['chromeosdevices'])
        if matches > 1:
            return self.GoogleAsset(RaidResponse('301').json)
        return self.GoogleAsset(results['chromeosdevices'][0])

    def update_asset(self, attr, serial, new_data):
        """Updates asset's provided attribute in Google. See Google Admin SDK API docs for valid attribute names.
        Returns RaidAsset object."""
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
        return self.GoogleAsset(RaidResponse('400').json)

    def update_asset_name(self, serial, new_name):
        """Updates asset's name (Asset ID in Google speak) in Google.
        Returns RaidAsset object."""
        return self.update_asset("annotatedAssetId", serial, new_name)

    def update_asset_tag(self, serial, new_tag):
        """Updates asset's inventory tag number (Notes field) in Google.
        Returns RaidAsset object."""
        return self.update_asset("notes", serial, new_tag)

    def update_asset_org(self, serial, new_org):
        """Updates asset's OU in Google.
        Returns RaidAsset object."""
        result = self.get_device_id(serial)
        if result:
            payload = {
                'deviceIds': [
                    result
                ]
            }
            try:
                self.service.chromeosdevices().moveDevicesToOu(customerId="my_customer",
                                                                      orgUnitPath=new_org,
                                                                      body=payload).execute()
            except HttpError:
                return self.GoogleAsset(RaidResponse('501').json)
            else:
                return self.GoogleAsset(RaidResponse('200').json)
        return self.GoogleAsset(RaidResponse('302').json)

    def get_device_id(self, serial):
        """Returns assets Google device ID if found, otherwise returns None."""
        result = self.search(serial)
        if result.raid_code['code'] == '200':
            return result.deviceId
        return None
