from ..api import (AssetApi, ConversationApi, MessageApi, NetworkApi, PinApi,
                   TransferApi, UserApi)
from ..common.constants import CONST
from . import _requests, _sign
from ._api_interface import ApiInterface
from .bot_config import BotConfig


class HttpClient_WithouAuth:
    """HTTP Client without auth token,
    for convenient access to public Mixin APIs.
    """

    def __init__(self, host_uri: str = CONST.API_HOST_DEFAULT):
        self.http = _requests.HttpRequest(host_uri, self._get_auth_token)
        self.api = ApiInterface(network_api=NetworkApi(self.http))

    def _get_auth_token(self, *args, **kwargs):  # ignore arguments
        return None


class HttpClient_UserAuth:
    """HTTP Client (with user's oauth token)"""

    def __init__(self, auth_token: str, host_uri: str = CONST.API_HOST_DEFAULT):
        self.auth_token = auth_token
        self.http = _requests.HttpRequest(host_uri, self._get_auth_token)
        self.api = ApiInterface(user_api=UserApi(self.http))

    def _get_auth_token(self, *args, **kwargs):  # ignore arguments
        return self.auth_token


class HttpClient_BotAuth:
    """HTTP Client with bot config"""

    def __init__(self, config: BotConfig, host_uri: str = CONST.API_HOST_DEFAULT):
        self.config = config
        self.http = _requests.HttpRequest(host_uri, self._get_auth_token)
        self.api = ApiInterface(
            user_api=UserApi(self.http),
            message_api=MessageApi(self.http),
            asset_api=AssetApi(self.http),
            pin_api=PinApi(self.http),
            conversation_api=ConversationApi(self.http),
            transfer_api=TransferApi(self.http, self.get_encrypted_pin),
        )

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
