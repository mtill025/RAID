# TODO: Docstrings for all methods
# TODO: Implement return type standards for all methods
# TODO: Test all methods for both success and failure
# TODO: Comments


class RaidResponse:

    def __init__(self, code):
        messages = {
            'r200': 'Operation completed successfully.',
            's302': 'No assets matched query.',
            's400': 'Update Property failed.',
            's401': 'Asset tag already exists.',
            'g301': 'More than one asset matched query.',
            'g302': 'No assets matched query.',
            'g400': 'Update property failed.',
            'g401': 'Move asset to OU failed.',
        }
        self.json = {
            'raid_code': {
                'code': code,
                'message': messages[code],
            }
        }


class RaidAsset:
    def __init__(self, assetinfo):
        self.dict = assetinfo
        if 'raid_code' not in self.dict:
            self.dict['raid_code'] = RaidResponse('r200').json['raid_code']
        for key in assetinfo:
            setattr(self, key, assetinfo[key])
