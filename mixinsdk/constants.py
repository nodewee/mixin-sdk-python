from dataclasses import dataclass


@dataclass(frozen=True)
class _ApiBaseUrls:
    HTTP_DEFAULT: str = "https://api.mixin.one"
    HTTP_ZEROMESH: str = "https://mixin-api.zeromesh.net"
    BLAZE_DEFAULT: str = "wss://blaze.mixin.one"
    BLAZE_ZEROMESH: str = "wss://mixin-blaze.zeromesh.net"


API_BASE_URLS = _ApiBaseUrls()


BUTTON_COLORS = [
    "7983C2",
    "8F7AC5",
    "C5595A",
    "C97B46",
    "76A048",
    "3D98D0",
    "5979F0",
    "8A64D0",
    "B76753",
    "AA8A46",
    "9CAD23",
    "6BC0CE",
    "6C89D3",
    "AA66C3",
    "C8697D",
    "C49B4B",
    "5FB05F",
    "52A98B",
    "75A2CB",
    "A75C96",
    "9B6D77",
    "A49373",
    "6AB48F",
    "93B289",
]
