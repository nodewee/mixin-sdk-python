import json
import urllib.parse
import uuid
from base64 import b64encode
from collections import namedtuple
from dataclasses import dataclass


@dataclass(frozen=True)
class _SharingCategory:
    TEXT: str = "text"
    POST: str = "post"
    IMAGE: str = "image"
    CONTACT: str = "contact"
    APP_CARD: str = "app_card"
    LIVE: str = "live"


SHARING_CATEGORIES = _SharingCategory()


SharingDataObject = namedtuple(
    "SharingDataObject", ["payload", "b64encoded_data", "category"]
)


def generate_sharing_uri(
    sharing_data: SharingDataObject, conversation_id: str = None
) -> str:
    uri = f"mixin://send?category={sharing_data.category}"
    uri += f"&data={sharing_data.b64encoded_data}"
    if conversation_id:
        uri += f"&conversation_id={conversation_id}"
    return uri


def pack_sharing_text(text: str):
    payload = text
    data = b64encode(text.encode("utf-8")).decode("utf-8")
    return SharingDataObject(payload, data, SHARING_CATEGORIES.TEXT)


def pack_sharing_post(markdown_text: str):
    payload = markdown_text
    data = b64encode(markdown_text.encode("utf-8")).decode("utf-8")
    return SharingDataObject(payload, data, SHARING_CATEGORIES.POST)


def pack_sharing_image(image_url: str):
    payload = {"url": image_url}
    data = b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    return SharingDataObject(payload, data, SHARING_CATEGORIES.IMAGE)


def pack_sharing_contact(user_id: str):
    payload = {"user_id": user_id}
    data = b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    return SharingDataObject(payload, data, SHARING_CATEGORIES.CONTACT)


def pack_sharing_app_card(
    action: str, app_id: str, description: str, icon_url: str, title: str
):
    payload = {
        "action": action,
        "app_id": app_id,
        "description": description,
        "icon_url": icon_url,
        "title": title,
    }
    data = b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    return SharingDataObject(payload, data, SHARING_CATEGORIES.APP_CARD)


def pack_sharing_live(height: int, width: int, url: str, thumb_url: str):
    payload = {
        "height": height,
        "width": width,
        "url": url,
        "thumb_url": thumb_url,
    }
    data = b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    return SharingDataObject(payload, data, SHARING_CATEGORIES.LIVE)


# -----


def pack_input_action(text: str, at_mixin_number: str = None) -> str:
    """
    Arguments:
    - at_mixin_number: str, optional,
        use in group conversation to mention a specific user
    """
    action = "input:"
    if at_mixin_number:
        action += f"@{at_mixin_number} "
    action += text
    return action


# -----


def pack_payment_uri(
    recipient_id: str,
    asset_id: str,
    amount: str,
    memo: str = None,
    trace_id: str = None,
) -> str:
    """
    - recipient_id, *required*, user id of the receiver
    - asset_id, *required*
    - amount, *required*, e.g.: "0.01", supports up to 8 digits after the decimal point
    - memo, optional, maximally 140 characters
    - trace_id, optional, used to prevent duplicate payment.
        If not specified, a random UUID will be generated.
    """

    trace_id = trace_id if trace_id else str(uuid.uuid4())
    amount = amount if isinstance(amount, str) else f"{amount:.8f}"
    uri = f"mixin://pay?recipient={recipient_id}&asset={asset_id}"
    uri += f"&amount={amount}&trace={trace_id}"
    if memo:
        uri += f"&memo={urllib.parse.quote(memo)}"
    return uri


# TODO: more payment schema types


# TODO: other schema types
