import requests
from AWAuth import AWAuth


class AirWatchController:

    class AWAsset:
        def __init__(self, assetinfo):
            self.dict = assetinfo
            for key in assetinfo:
                setattr(self, key, assetinfo[key])

    def __init__(self, api_url):
        airwatch = AWAuth()
        self.AW_AUTH = airwatch.cred
        self.AW_KEY = airwatch.key
        self.api_url = api_url

    def req(self, method, url, headers=None, json=None, params=None):
        """Formats an API call to AirWatch using the requests module with some common parameters set to default
        values. """
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
        """Searches AirWatch for serial number. Returns AWAsset object if it is found,
        otherwise returns None."""
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
        return None

    def get_airwatch_id(self, serial):
        """Searches AirWatch for serial number. Returns AirWatch ID of asset if it is found,
        otherwise returns None."""
        asset = self.search(serial)
        if asset is not None:
            return asset.Id["Value"]
        return None

    def update_asset(self, serial, updates: dict):
        """Updates the fields in AirWatch defined in the updates parameter for a given serial number.
        See AirWatch API docs for valid field names.
        Returns the request status code."""
        aw_id = self.get_airwatch_id(serial)
        response = self.req(
            method="put",
            url=f"/mdm/devices/{aw_id}",
            json=updates,
        )
        return response.status_code

    def update_asset_tag(self, serial, asset_tag):
        """Updates the Asset Number field in AirWatch for a given serial number.
        Returns the request status code."""
        aw_id = self.get_airwatch_id(serial)
        response = self.req(
            method="put",
            url=f"/mdm/devices/{aw_id}",
            json={
                "AssetNumber": asset_tag,
            }
        )
        return response.status_code

    def update_asset_name(self, serial, name):
        """Updates the Asset Friendly Name field in AirWatch for a given serial number.
        Returns the request status code."""
        aw_id = self.get_airwatch_id(serial)
        response = self.req(
            method="put",
            url=f"/mdm/devices/{aw_id}",
            json={
                "DeviceFriendlyName": name,
            }
        )
        return response.status_code

    def update_asset_org(self, serial, org):
        """Updates the Org Group in AirWatch for a given serial number.
                Returns the request status code."""
        aw_id = self.get_airwatch_id(serial)
        new_org = self.req(
            method="get",
            url="/system/groups/search",
            params={
                "Name": org,
            }
        )
        if new_org.status_code != 200:
            return new_org.status_code
        new_org_id = new_org.json()["LocationGroups"][0]["Id"]["Value"]
        response = self.req(
            method="put",
            url=f"/mdm/devices/{aw_id}/commands/changeorganizationgroup/{new_org_id}",
        )
        return response.status_code

    def get_smart_groups(self, serial):
        aw_id = self.get_airwatch_id(serial)
        response = self.req(
            method="get",
            url=f"/mdm/devices/{aw_id}/smartgroups",
        )
        return response.json()

