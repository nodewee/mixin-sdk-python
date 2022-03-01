import base64
import datetime
from typing import Union


def base64_encode(s: bytes):
    """Use url-safe-alphabet uniformly"""
    return base64.urlsafe_b64encode(s)


def base64_decode(s: Union[bytes, str]):
    """Use url-safe-alphabet uniformly"""
    return base64.urlsafe_b64decode(s)


def base64_pad_equal_sign(s: str):
    if not len(s) % 4 == 0:
        s = s + "===="
    return s


def parse_rfc3339_to_datetime(s: str):
    """
    -s, RFC3339Nano format, e.g. `2020-12-12T12:12:12.999999999Z`
    """
    [datestr, timestr] = s.split("T")
    [year, month, day] = datestr.split("-")
    [hour, minute, second] = timestr.split(":")
    [second, nanosec] = second.split(".")
    microsec = int(nanosec.rstrip("Z")[:6])

    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        int(microsec),
    )
