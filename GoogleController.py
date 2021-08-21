from GoogleAuth import GoogleAuth
from googleapiclient.discovery import build
from RaidResponse import RaidResponse


class GoogleController:
    class GoogleAsset:
        def __init__(self, assetinfo):
            self.dict = assetinfo
            for key in assetinfo:
                setattr(self, key, assetinfo[key])

    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/admin.directory.device.chromeos',
                  'https://www.googleapis.com/auth/admin.directory.orgunit']
        self.google_auth = GoogleAuth(scopes)
        if not self.google_auth.credentials:
            self.google_auth.initialize_oauth()
        self.service = build('admin', 'directory_v1', credentials=self.google_auth.credentials)

    def search(self, serial):
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
        if 'raid_code' not in result.dict:
            return result.deviceId
        return None
