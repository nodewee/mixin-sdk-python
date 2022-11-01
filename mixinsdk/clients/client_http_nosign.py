from ..constants import API_BASE_URLS
from . import _requests


class HttpClient_WithoutAuth:
    """HTTP Client without authentication,
    for convenient access to public Mixin APIs.
    """

    class _ApiInterface:
        def __init__(self, http):
            # imports Api Classes only when it's required
            from ..api.network import NetworkApi

            self.network = NetworkApi(http)

    def __init__(self, api_base: str = API_BASE_URLS.HTTP_DEFAULT):
        self.http = _requests.HttpRequest(api_base, self._get_auth_token)
        self.api = self._ApiInterface(self.http)

    def _get_auth_token(self, *args, **kwargs):  # ignore arguments
        return None


class HttpClient_WithAccessToken:
    class _ApiInterface:
        def __init__(self, http):
            from ..api.user import UserApi

            self.user = UserApi(http)

    def __init__(self, access_token: str, api_base: str = API_BASE_URLS.HTTP_DEFAULT):
        self.auth_token = access_token
        self.http = _requests.HttpRequest(api_base, self._get_auth_token)
        self.api = self._ApiInterface(self.http)

    def _get_auth_token(self, *args, **kwargs):  # ignore arguments
        return self.auth_token
