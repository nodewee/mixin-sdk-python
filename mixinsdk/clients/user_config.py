import json
from base64 import urlsafe_b64decode

from ..utils import base64_pad_equal_sign


class AppConfig:
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
    def from_payload(cls, payload: dict) -> "AppConfig":
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

        if isinstance(payload, str):
            payload = json.loads(payload)

        c = cls(
            payload.get("pin"),
            payload["client_id"],
            payload["session_id"],
            payload["pin_token"],
            payload["private_key"],
            payload.get("mixin_id"),
            payload.get("client_secret"),
            payload.get("name"),
        )
        return c

    @classmethod
    def from_file(cls, file_path: str) -> "AppConfig":
        with open(file_path, "rt") as f:
            return cls.from_payload(f.read())


class NetworkUserConfig:
    """
    Config object of mixin network user(created by application user)
    """

    def __init__(
        self,
        user_id,
        session_id,
        pin,
        pin_token,
        private_key,
        public_key,
    ):
        """
        - private_key/public_key: must be base64 encoded Ed25519 key
        """
        self.user_id = user_id
        self.session_id = session_id
        self.pin = pin
        self.pin_token = base64_pad_equal_sign(pin_token)
        self.private_key = urlsafe_b64decode(
            base64_pad_equal_sign(private_key).encode()
        )
        if public_key:
            self.public_key = urlsafe_b64decode(
                base64_pad_equal_sign(public_key).encode()
            )
        else:
            self.public_key = None

        self.key_algorithm = "Ed25519"

    @classmethod
    def from_payload(cls, payload: dict) -> "AppConfig":
        """
        payload structure:
        {
            "user_id": "required",
            "session_id": "required",
            "pin": "",
            "pin_token": "required",
            "private_key": "required",
            "public_key": "",
        }
        """

        if isinstance(payload, str):
            payload = json.loads(payload)

        c = cls(
            payload["user_id"],
            payload["session_id"],
            payload.get("pin"),
            payload["pin_token"],
            payload["private_key"],
            payload.get("public_key"),
        )
        return c

    @classmethod
    def from_file(cls, file_path: str) -> "AppConfig":
        with open(file_path, "rt") as f:
            return cls.from_payload(f.read())
