import keyring
import base64


class AWAuth:

    def __init__(self):
        self.cred = "Basic " + str(base64.b64encode(keyring.get_password("aw_auth", "authcode").encode("ascii"))).split("'")[1]
        self.key = keyring.get_password("aw_key", "key")
