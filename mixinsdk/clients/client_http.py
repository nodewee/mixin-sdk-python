import base64
import hashlib
import time

from ..constants import API_BASE_URLS
from ..utils import get_conversation_id_of_two_users
from . import _message, _requests, _sign
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

            # methods of high-frequency use are assigned to self
            self.send_messages = self.message.send_messages

    def __init__(self, config: AppConfig, api_base: str = API_BASE_URLS.HTTP_DEFAULT):
        self.config = config
        self.http = _requests.HttpRequest(api_base, self._get_auth_token)
        self.api = self._ApiInterface(self.http, self.get_current_encrypted_pin)

        self._conversation_user_sessions = {}  # {id:{expire_at, sessions}}

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

    def parse_message_data(self, data: str, category: str):
        return _message.parse_message_data(
            data, category, self.config.session_id, self.config.private_key
        )

    def encrypt_message_data(self, b64encoded_data: str, conversation_id: str):
        data_bytes = base64.b64decode(b64encoded_data)
        user_sessions = self.get_conversation_user_sessions(conversation_id)
        # print("\n\nGot user_sessions:", user_sessions)
        encrypted_data = _message.encrypt_message_data(
            data_bytes, user_sessions, self.config.private_key
        )
        recipient_sessions = [
            {"session_id": session["session_id"]} for session in user_sessions
        ]
        # print(recipient_sessions)
        # exit()
        checksum = self.generate_session_checksum(recipient_sessions)

        return encrypted_data, recipient_sessions, checksum

    def generate_session_checksum(self, sessions: list[dict]):
        # sort sessions by session_id
        sorted_sessions = sorted(sessions, key=lambda s: s["session_id"])
        md5 = hashlib.md5()
        for s in sorted_sessions:
            md5.update(s["session_id"].encode("utf-8"))
        return md5.hexdigest()

    def get_conversation_user_sessions(self, conversation_id: str):
        """
        - conversation_id: str
        """
        conv = self.api.conversation.read(conversation_id)
        # print("\n\nconversation:", conv)
        sessions = conv["data"]["participant_sessions"]
        return sessions
        #
        if conversation_id in self._conversation_user_sessions:
            d = self._conversation_user_sessions[conversation_id]
            if d["expire_at"] > time.time():
                return d["sessions"]
            else:
                del self._conversation_user_sessions[conversation_id]
                return self.get_conversation_user_sessions(conversation_id)
        else:
            sessions = self.api.conversation.read(conversation_id)["data"][
                "participant_sessions"
            ]
            # cache
            expire_at = time.time() + 3600  # every hour to read from api again
            d = {
                "expire_at": expire_at,
                "sessions": sessions,
            }
            self._conversation_user_sessions[conversation_id] = d

            return sessions


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
