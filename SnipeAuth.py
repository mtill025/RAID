import keyring


class SnipeAuth:

    def __init__(self):
        self.auth = keyring.get_password("snipe_key", "key")

