# TODO: Docstrings for all methods
# TODO: Test all methods for both success and failure
# TODO: Comments
# TODO: Settings file
# TODO: Implement success checks for all put methods in all controllers


class RaidResponse:

    def __init__(self, code):
        messages = {
            'r100': 'Unknown error code: ',
            'r101': 'Request submitted with unknown result.',
            'a401': 'New org not found.',
            'a500': 'Search failed.',
            'r200': 'Operation completed successfully.',
            's302': 'No assets matched query.',
            's400': 'Update property failed.',
            's401': 'Asset tag already exists.',
            'g301': 'More than one asset matched query.',
            'g302': 'No assets matched query.',
            'g400': 'Update property failed.',
            'g401': 'Move asset to OU failed.',
        }
        if code not in messages:
            messages['r100'] = messages['r100'] + code
            code = 'r100'
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
