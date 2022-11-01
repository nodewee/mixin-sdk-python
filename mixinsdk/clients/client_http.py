from ..constants import API_BASE_URLS
from ..utils import get_conversation_id_of_two_users
from . import _requests, _sign
from .config import AppConfig, NetworkUserConfig


class HttpClient_WithAppConfig:
    class _ApiInterface:
        def __init__(self, http, get_current_encrypted_pin: callable):

            # imports Api Classes only when it's required
            from ..api.asset import AssetApi
            from ..api.conversation import ConversationApi
            from ..api.message import MessageApi
            from ..api.network import NetworkApi
            from ..api.pin import PinApi
            from ..api.transfer import TransferApi
            from ..api.user import UserApi

            self.user = UserApi(http)
            self.message = MessageApi(http)
            self.asset = AssetApi(http)
            self.pin = PinApi(http)
            self.conversation = ConversationApi(http)
            self.transfer = TransferApi(http, get_current_encrypted_pin)
            self.network = NetworkApi(http)

            # methods of high-frequency use
            self.send_messages = self.message.send_messages

    def __init__(self, config: AppConfig, api_base: str = API_BASE_URLS.HTTP_DEFAULT):
        self.config = config

        self.http = _requests.HttpRequest(api_base, self._get_auth_token)
        self.api = self._ApiInterface(self.http, self.get_current_encrypted_pin)

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

    def get_conversation_id_with_user(self, user_id: str):
        return get_conversation_id_of_two_users(self.config.client_id, user_id)

    def get_current_encrypted_pin(self):
        return self.encrypt_pin(self.config.pin)

    def encrypt_pin(self, pin: str):
        """
        - pin: str, 6 digits number
        """
        if not pin:
            return None
        cfg = self.config
        return _sign.encrypt_pin(
            pin, cfg.pin_token, cfg.private_key, cfg.key_algorithm, cfg.session_id
        )


class HttpClient_WithNetworkUserConfig:
    class _ApiInterface:
        def __init__(self, http, get_current_encrypted_pin: callable):

            # imports Api Classes only when it's required
            from ..api.asset import AssetApi
            from ..api.network import NetworkApi
            from ..api.pin import PinApi
            from ..api.transfer import TransferApi
            from ..api.user import UserApi

            self.user = UserApi(http)
            self.asset = AssetApi(http)
            self.pin = PinApi(http)
            self.transfer = TransferApi(http, get_current_encrypted_pin)
            self.network = NetworkApi(http)

    def __init__(
        self, config: NetworkUserConfig, api_base: str = API_BASE_URLS.HTTP_DEFAULT
    ):
        self.config = config
        self.http = _requests.HttpRequest(api_base, self._get_auth_token)
        self.api = self._ApiInterface(self.http, self.get_current_encrypted_pin)

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

    def get_current_encrypted_pin(self):
        return self.encrypt_pin(self.config.pin)

    def encrypt_pin(self, pin: str):
        """
        - pin: str, 6 digits number
        """
        if not pin:
            return None
        cfg = self.config
        return _sign.encrypt_pin(
            pin, cfg.pin_token, cfg.private_key, cfg.key_algorithm, cfg.session_id
        )
