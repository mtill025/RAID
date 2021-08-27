# TODO: Settings file


class RaidResponse:

    def __init__(self, code, api_code="", api_msg=""):
        messages = {
            '100': 'Unknown error code: ',
            '101': 'Request submitted with unknown result.',
            '501': 'New org not found.',
            '500': 'Search failed.',
            '200': 'Operation completed successfully.',
            '302': 'No assets matched query.',
            '400': 'Update property failed.',
            '401': 'Asset tag already exists.',
            '301': 'More than one asset matched query.',
        }
        if code not in messages:
            messages['100'] = messages['100'] + code
            code = '100'
        self.json = {
            'raid_code': {
                'code': code,
                'message': messages[code],
                'api_code': api_code,
                'api_message': api_msg,
            }
        }


class RaidAsset:
    def __init__(self, assetinfo: dict):
        self.dict = assetinfo
        self.platform = "RAID"
        if 'raid_code' not in self.dict:
            self.dict['raid_code'] = RaidResponse('200').json['raid_code']
        for key in assetinfo:
            setattr(self, key, assetinfo[key])


class RaidSettings:
    def __init__(self, settings_dict):
        for key in settings_dict:
            setattr(self, key, settings_dict[key])

