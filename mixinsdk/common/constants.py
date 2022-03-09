from dataclasses import dataclass


@dataclass(frozen=True)
class _ApiBaseUrls:
    HTTP: str = "https://api.mixin.one"
    HTTP_ZEROMESH: str = "https://mixin-api.zeromesh.net"
    BLAZE_DEFAULT: str = "wss://blaze.mixin.one"
    BLAZE_ZEROMESH: str = "wss://mixin-blaze.zeromesh.net"


API_BASE_URLS = _ApiBaseUrls()
