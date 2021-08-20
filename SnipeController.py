import requests
from SnipeAuth import SnipeAuth


class SnipeController:

    class SnipeAsset:
        def __init__(self, assetinfo):
            self.dict = assetinfo
            for key in assetinfo:
                setattr(self, key, assetinfo[key])

    def __init__(self, api_url):
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
        url = f"/hardware/byserial/{serial}"
        response = self.req(
            method="get",
            url=url,
        )
        if response.status_code == 200 and response.json()['rows'] != []:
            return self.SnipeAsset(response.json()['rows'][0])
        else:
            return None

    def get_snipe_id(self, serial):
        asset = self.search(serial)
        if asset:
            return asset.dict['id']
        return None

    def update_asset_name(self, serial, new_name):
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
        return response.json()

    def update_asset_company(self, serial, new_company):
        snipe_id = self.get_snipe_id(serial)
        url = f"/hardware/{snipe_id}"
        company_id = self.get_company_id(new_company)
        json = {
            "company_id": company_id
        }
        if company_id is not None:
            response = self.req(
                method="put",
                url=url,
                json=json,
            )
            return response.json()
        return {'status': 'error'}

    def update_asset_tag(self, serial, new_tag):
        if "id" in self.search_by_asset_tag(new_tag):
            return {
                "status": "error",
                "message": "Asset tag already exists"
            }
        snipe_id = self.get_snipe_id(serial)
        url = f"/hardware/{snipe_id}"
        json = {
            "asset_tag": new_tag
        }
        response = self.req(
            method="put",
            url=url,
            json=json,
        )
        return response.json()

    def search_by_asset_tag(self, asset_tag):
        url = f"/hardware/bytag/{asset_tag}"
        response = self.req(
            method="get",
            url=url,
        )
        return response.json()

    def get_companies(self):
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
        companies = self.get_companies()
        for company in companies['rows']:
            if req_company == company['name']:
                return company['id']
        return None











