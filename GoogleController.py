from GoogleAuth import GoogleAuth
from googleapiclient.discovery import build


class GoogleController:

    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/admin.directory.device.chromeos',
                  'https://www.googleapis.com/auth/admin.directory.orgunit']
        self.google_auth = GoogleAuth(scopes)
        if not self.google_auth.credentials:
            self.google_auth.initialize_oauth()

    def search(self, serial):
        service = build('admin', 'directory_v1', credentials=self.google_auth.credentials)
        results = service.chromeosdevices().list(customerId="my_customer", query=serial,
                                                 projection="BASIC").execute()
        return results


