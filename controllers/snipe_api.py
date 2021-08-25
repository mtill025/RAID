import requests
import keyring
from raid import RaidAsset, RaidResponse


class SnipeAuth:

    def __init__(self):
        self.auth = keyring.get_password("snipe_key", "key")


class SnipeController:

    class SnipeAsset(RaidAsset):
        def __init__(self, assetinfo):
            super().__init__(assetinfo)
            self.platform = "Snipe"

    def __init__(self, api_url):
        """Wrapper for interacting with the Snipe API."""
        snipe = SnipeAuth()
        self.auth = snipe.auth
        self.api_url = api_url

    def req(self, method, url, headers=None, json=None, params=None):
        """Formats an API call to Snipe using the requests module with some common parameters set to default
        values. """
        def_header = {
            "Authorization": self.auth,
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
        """Searches Snipe for serial number.
        Returns RaidAsset object."""
        url = f"/hardware/byserial/{serial}"
        response = self.req(
            method="get",
            url=url,
        )
        json = response.json()
        if response.status_code == 200 and json['rows'] != []:
            return self.SnipeAsset(json['rows'][0])
        return self.SnipeAsset(RaidResponse('302', json['messages']).json)

    def search_by_asset_tag(self, asset_tag):
        """Searches Snipe for asset tag.
        Returns RaidAsset object."""
        url = f"/hardware/bytag/{asset_tag}"
        response = self.req(
            method="get",
            url=url,
        )
        if 'status' not in response.json():
            return self.SnipeAsset(response.json())
        return self.SnipeAsset(RaidResponse('302').json)

    def get_snipe_id(self, serial):
        """Returns Snipe ID for serial provided if found, otherwise returns None."""
        asset = self.search(serial)
        if asset.raid_code['code'] == '200':
            return asset.dict['id']
        return None

    def get_companies(self):
        """Returns dictionary of companies currently in Snipe."""
        url = "/companies"
        response = self.req(
            method="get",
            url=url,
        )
        companies = response.json()
        companies['names'] = []
        for company in companies['rows']:
            companies['names'].append(company['name'])
        return companies

    def get_company_id(self, req_company):
        """Returns Snipe company ID for company provided if found, otherwise returns None."""
        companies = self.get_companies()
        for company in companies['rows']:
            if req_company == company['name']:
                return company['id']
        return None

    def update_asset_name(self, serial, new_name):
        """Updates asset's name in Snipe.
        Returns RaidAsset object."""
        snipe_id = self.get_snipe_id(serial)
        url = f"/hardware/{snipe_id}"
        json = {
            "name": new_name
        }
        response = self.req(
            method="put",
            url=url,
            json=json,
        )
        if snipe_id:
            return self.SnipeAsset(response.json())
        return self.SnipeAsset(RaidResponse('400').json)

    def update_asset_company(self, serial, new_company):
        """Updates asset's company in Snipe.
        Returns RaidAsset object."""
        snipe_id = self.get_snipe_id(serial)
        url = f"/hardware/{snipe_id}"
        company_id = self.get_company_id(new_company)
        json = {
            "company_id": company_id
        }
        if company_id is not None and snipe_id is not None:
            response = self.req(
                method="put",
                url=url,
                json=json,
            )
            return self.SnipeAsset(response.json())
        return self.SnipeAsset(RaidResponse('400').json)

    def update_asset_tag(self, serial, new_tag):
        """Updates asset's inventory tag number in Snipe.
        Returns RaidAsset object."""
        if "id" in self.search_by_asset_tag(new_tag).dict:
            return self.SnipeAsset(RaidResponse('401').json)
        snipe_id = self.get_snipe_id(serial)
        url = f"/hardware/{snipe_id}"
        json = {
            "asset_tag": new_tag
        }
        if snipe_id is not None:
            response = self.req(
                method="put",
                url=url,
                json=json,
            )
            return self.SnipeAsset(response.json())
        return self.SnipeAsset(RaidResponse('400').json)















