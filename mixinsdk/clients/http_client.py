from ..common.constants import CONST
from . import _requests, _sign
from .bot_config import BotConfig


class HttpClient_WithoutAuth:
    """HTTP Client without auth token,
    for convenient access to public Mixin APIs.
    """

    class _ApiInterface:
        def __init__(self, http):
            # imports Api Classes only when it's required
            from ..api.network import NetworkApi

            self.network = NetworkApi(http)

    def __init__(self, host_uri: str = CONST.API_HOST_DEFAULT):
        self.http = _requests.HttpRequest(host_uri, self._get_auth_token)
        self.api = self._ApiInterface(self.http)

    def _get_auth_token(self, *args, **kwargs):  # ignore arguments
        return None


class HttpClient_UserAuth:
    """HTTP Client (with user's oauth token)"""

    class _ApiInterface:
        def __init__(self, http):
            from ..api.user import UserApi

            self.user = UserApi(http)

    def __init__(self, auth_token: str, host_uri: str = CONST.API_HOST_DEFAULT):
        self.auth_token = auth_token
        self.http = _requests.HttpRequest(host_uri, self._get_auth_token)
        self.api = self._ApiInterface(self.http)

    def _get_auth_token(self, *args, **kwargs):  # ignore arguments
        return self.auth_token


class HttpClient_BotAuth:
    """HTTP Client with bot config"""

    class _ApiInterface:
        def __init__(self, http, get_encrypted_pin: callable):

            # imports Api Classes only when it's required
            from ..api.user import UserApi
            from ..api.message import MessageApi
            from ..api.asset import AssetApi
            from ..api.pin import PinApi
            from ..api.conversation import ConversationApi
            from ..api.transfer import TransferApi

            self.user = UserApi(http)
            self.message = MessageApi(http)
            self.asset = AssetApi(http)
            self.pin = PinApi(http)
            self.conversation = ConversationApi(http)
            self.transfer = TransferApi(http, get_encrypted_pin)

    def __init__(self, config: BotConfig, host_uri: str = CONST.API_HOST_DEFAULT):
        self.config = config
        self.http = _requests.HttpRequest(host_uri, self._get_auth_token)
        self.api = self._ApiInterface(self.http, self.get_encrypted_pin)

    def _get_auth_token(self, method: str, uri: str, bodystring: str):
        return _sign.sign_authentication_token(
            self.config.client_id,
            self.config.session_id,
            self.config.private_key,
            self.config.key_algorithm,
            method,
            uri,
            bodystring,
        )

    def get_encrypted_pin(self):
        cfg = self.config
        return _sign.encrypt_pin(
            cfg.pin, cfg.pin_token, cfg.private_key, cfg.key_algorithm, cfg.session_id
        )
