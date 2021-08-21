
class RaidResponse:

    def __init__(self, code):
        messages = {
            'g301': 'More than one asset matched query.',
            'g302': 'No assets matched query.',
            'g400': 'Update property failed.',
            'g401': 'Move asset to OU failed.',
        }
        self.json = {
            'raid_code': code,
            'message': messages[code],
        }
