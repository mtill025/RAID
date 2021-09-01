import requests
import keyring
import base64
from raid import RaidAsset, RaidResponse


class AWAuth:

    def __init__(self):
        self.cred = "Basic " + str(base64.b64encode(keyring.get_password("aw_auth", "authcode").encode("ascii"))).split("'")[1]
        self.key = keyring.get_password("aw_key", "key")


class AirWatchController:

    class AWAsset(RaidAsset):
        def __init__(self, assetinfo):
            super().__init__(assetinfo)
            self.platform = "AirWatch"
            if 'SerialNumber' in self.dict:
                self.serial = self.SerialNumber
            if 'DeviceFriendlyName' in self.dict:
                self.name = self.DeviceFriendlyName
            if 'AssetNumber' in self.dict:
                self.asset_tag = self.AssetNumber
            if 'LocationGroupName' in self.dict:
                self.org_unit = self.LocationGroupName

    def __init__(self, api_url):
        """Wrapper for interacting with the AirWatch API."""
        airwatch = AWAuth()
        self.AW_AUTH = airwatch.cred
        self.AW_KEY = airwatch.key
        self.api_url = api_url
        self.platform = "AirWatch"

    def req(self, method, url, headers=None, json=None, params=None):
        """Formats an API call to AirWatch using the requests module with some common parameters set to default
        values.
         Returns the entire request response object or None if invalid parameters were provided."""
        def_header = {
            "Authorization": self.AW_AUTH,
            "aw-tenant-code": self.AW_KEY,
            "Accept": "application/json",
        }
        endp = f"{self.api_url}{url}"
        if headers is not None:
            for key in headers:
                def_header[key] = headers["key"]
        if method == "get":
            if params is None:
                params = {}
            response = requests.get(
                url=endp,
                headers=def_header,
                params=params
            )
            return response
        elif method == "put":
            if json is None:
                json = {}
            response = requests.put(
                url=endp,
                headers=def_header,
                json=json,
            )
            return response
        else:
            return None

    def search(self, serial):
        """Searches AirWatch for serial number. Returns RaidAsset object."""
        response = self.req(
            method="get",
            url="/mdm/devices",
            params={
                "searchBy": "Serialnumber",
                "id": serial,
            }
        )
        if response.status_code == 200:
            asset_info = response.json()
            return self.AWAsset(asset_info)
        return self.AWAsset(RaidResponse('500').json)

    def get_airwatch_id(self, serial):
        """Searches AirWatch for serial number. Returns AirWatch ID of asset if it is found,
        otherwise returns None."""
        asset = self.search(serial)
        if asset.raid_code['code'] == '200':
            return asset.Id["Value"]
        return None

    def update_asset(self, serial, updates: dict):
        """Updates the fields in AirWatch defined in the updates parameter for a given serial number.
        See AirWatch API docs for valid field names.
        Returns RaidAsset object with AW API response status code."""
        aw_id = self.get_airwatch_id(serial)
        response = self.req(
            method="put",
            url=f"/mdm/devices/{aw_id}",
            json=updates,
        )
        return self.AWAsset(RaidResponse('101', api_code=response.status_code).json)

    def update_asset_tag(self, serial, asset_tag):
        """Updates the Asset Number field in AirWatch for a given serial number.
        Returns RaidAsset object with AW API response status code."""
        json = {
            "AssetNumber": asset_tag,
        }
        return self.update_asset(serial, json)

    def update_asset_name(self, serial, name):
        """Updates the Asset Friendly Name field in AirWatch for a given serial number.
        Returns RaidAsset object with AW API response status code."""
        json = {
            "DeviceFriendlyName": name,
        }
        return self.update_asset(serial, json)

    def update_asset_org(self, serial, org):
        """Updates the Org Group in AirWatch for a given serial number.
         Returns RaidAsset object with AW API response status code."""
        aw_id = self.get_airwatch_id(serial)
        new_org = self.req(
            method="get",
            url="/system/groups/search",
            params={
                "Name": org,
            }
        )
        if new_org.status_code != 200:
            return self.AWAsset(RaidResponse('501').json)
        new_org_id = new_org.json()["LocationGroups"][0]["Id"]["Value"]
        response = self.req(
            method="put",
            url=f"/mdm/devices/{aw_id}/commands/changeorganizationgroup/{new_org_id}",
        )
        return self.AWAsset(RaidResponse('101', api_code=response.status_code).json)

    def get_smart_groups(self, serial):
        aw_id = self.get_airwatch_id(serial)
        response = self.req(
            method="get",
            url=f"/mdm/devices/{aw_id}/smartgroups",
        )
        return response.json()

