import json
from base64 import urlsafe_b64decode

from ..utils import base64_pad_equal_sign


class BotConfig:
    """
    Config object of Mixin applications
    (such as Mixin Messenger bot)
    """

    def __init__(
        self,
        pin,
        client_id,
        session_id,
        pin_token,
        private_key,
        mixin_id=None,
        client_secret=None,
        name=None,
    ):
        """You can get bot config value from https://developers.mixin.one/dashboard"""

        self.pin = pin
        self.client_id = client_id
        self.session_id = session_id
        self.pin_token = base64_pad_equal_sign(pin_token)
        self.private_key = private_key
        self.mixin_id = mixin_id
        self.client_secret = client_secret
        self.name = name
        #
        self.key_algorithm = ""  # Ed25519 or RS512 (EdDSA:Ed25519, RSA:RS512)
        if "RSA PRIVATE KEY" in self.private_key:
            self.key_algorithm = "RS512"
        else:
            self.key_algorithm = "Ed25519"
            key = base64_pad_equal_sign(self.private_key)
            self.private_key = urlsafe_b64decode(key.encode())

    @classmethod
    def from_payload(cls, payload: str) -> "BotConfig":
        """
        payload structure:
        {
            "pin": "",
            "client_id": "",
            "session_id": "",
            "pin_token": "",
            "private_key": "",
            "mixin_id": "",
            "client_secret": ""
            "name": ""
        }
        """

        d = json.loads(payload)
        c = cls(
            d["pin"],
            d["client_id"],
            d["session_id"],
            d["pin_token"],
            d["private_key"],
            d.get("mixin_id"),
            d.get("client_secret"),
            d.get("name"),
        )
        return c

    @classmethod
    def from_file(cls, file_path: str) -> "BotConfig":
        with open(file_path, "rt") as f:
            return cls.from_payload(f.read())
