from dataclasses import dataclass


@dataclass(frozen=True)
class _Constants:
    API_HOST_DEFAULT: str = "https://api.mixin.one"
    API_HOST_ZEROMESH: str = "https://mixin-api.zeromesh.net"
    BLAZE_HOST_DEFAULT: str = "wss://blaze.mixin.one"
    BLAZE_HOST_ZEROMESH: str = "wss://mixin-blaze.zeromesh.net"


CONST = _Constants()
