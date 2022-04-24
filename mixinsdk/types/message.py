import base64
import json
import uuid
from collections import namedtuple
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Union

import dacite

from ..utils import parse_rfc3339_to_datetime


@dataclass(frozen=True)
class _MessageCategory:
    TEXT: str = "PLAIN_TEXT"
    POST: str = "PLAIN_POST"

    STICKER: str = "PLAIN_STICKER"
    IMAGE: str = "PLAIN_IMAGE"
    AUDIO: str = "PLAIN_AUDIO"
    VIDEO: str = "PLAIN_VIDEO"
    LIVE: str = "PLAIN_LIVE"
    CONTACT: str = "PLAIN_CONTACT"
    LOCATION: str = "PLAIN_LOCATION"
    FILE: str = "PLAIN_DATA"

    APP_CARD: str = "APP_CARD"
    BUTTON_GROUP: str = "APP_BUTTON_GROUP"

    SYSTEM_ACCOUNT_SNAPSHOT: str = "SYSTEM_ACCOUNT_SNAPSHOT"
    SYSTEM_CONVERSATION: str = "SYSTEM_CONVERSATION"
    TRANSCRIPT: str = "PLAIN_TRANSCRIPT"  # ?

    MESSAGE_RECALL: str = "MESSAGE_RECALL"
    MESSAGE_PIN: str = "MESSAGE_PIN"


MESSAGE_CATEGORIES = _MessageCategory()

# ===== Message View =====


@dataclass
class MessageView:
    type: str
    representative_id: str
    quote_message_id: str
    conversation_id: str
    user_id: str
    session_id: str
    message_id: str
    category: str
    data: str
    status: str
    source: str
    silent: bool
    created_at: str
    updated_at: str

    def __post_init__(self):
        self.data_decoded = _parse_msg_data(self.data, self.category)
        self.created_at = parse_rfc3339_to_datetime(self.created_at)
        self.updated_at = parse_rfc3339_to_datetime(self.updated_at)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageView":
        return dacite.from_dict(cls, data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _parse_msg_data(data_str: str, category: str):
    """
    parse message data (Base64 encoded string) to str or dict

    Returns: parsed_data
    """
    if not data_str:
        return ""

    d = base64.b64decode(data_str).decode()
    if category in [MESSAGE_CATEGORIES.TEXT, MESSAGE_CATEGORIES.POST]:
        return d

    try:
        return json.loads(d)
    except json.JSONDecodeError:
        print(f"Failed to json decode data: {d}")


# ===== Message Request =====

MessageDataObject = namedtuple(
    "MessageDataObject", ["payload", "b64encoded_data", "category"]
)


def pack_message(
    data_obj: MessageDataObject,
    conversation_id: str,
    recipient_id: str = None,
    message_id: str = None,
    representative_id: str = None,
    quote_message_id: str = None,
):
    """
    - conversation_id, *required*
    - category, *required*
    - data, *required*, base64 encoded string of content payload
    - recipient_id, optional when send single message,
        *required* when send list of messages
    - message_id, optional, if not set, will be generated randomly
    """

    message_id = message_id if message_id else str(uuid.uuid4())
    pld = {
        "conversation_id": conversation_id,
        "category": data_obj.category,
        "data": data_obj.b64encoded_data,
        "message_id": message_id,
    }
    if recipient_id:
        pld["recipient_id"] = recipient_id
    if representative_id:
        pld["representative_id"] = representative_id
    if quote_message_id:
        pld["quote_message_id"] = quote_message_id

    return pld


def pack_text_data(text) -> MessageDataObject:
    payload = text
    return MessageDataObject(
        text,
        base64.b64encode(payload.encode("utf-8")).decode("utf-8"),
        MESSAGE_CATEGORIES.TEXT,
    )


def pack_post_data(markdown_text) -> MessageDataObject:
    payload = markdown_text
    b64encoded_data = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.POST)


def pack_sticker_data(sticker_id, album_id=None, name=None) -> MessageDataObject:
    payload = {"sticker_id": sticker_id}
    if album_id:
        payload["album_id"] = album_id
    if name:
        payload["name"] = name
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.STICKER)


def pack_contact_data(user_id) -> MessageDataObject:
    payload = {"user_id": user_id}
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.CONTACT)


def pack_button(label, action, color) -> dict:
    """
    Args:
    - label: button display text
    - action: URI, mixin schema or link, e.g. 'https://mixin.one'
    - color: hex color string, e.g. '#d53120'

    Return:
        payload:dict
    """

    payload = {"label": label, "action": action, "color": color}
    return payload


def pack_button_group_data(buttons: Union[Dict, List[Dict]]) -> MessageDataObject:
    """
    Args:
        - buttons, list of button payload

    Return (payload, b64encoded_data, category)
    """
    if isinstance(buttons, Dict):
        buttons = [buttons]
    payload = buttons
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.BUTTON_GROUP)


def pack_image_data(
    attachment_id: str,
    mime_type: str,
    size: int,
    width: int = None,
    height: int = None,
    thumbnail: str = None,
):
    """
    Args:
        attachment_id: read From POST /attachments
        mime_type: e.g. "image/jpeg"
        size: image data bytes size
        thumbnail: "base64 encoded"

    Return (payload, b64encoded_data, category)
    """
    payload = {
        "attachment_id": attachment_id,
        "mime_type": mime_type,
        "width": width,
        "height": height,
        "size": size,
        "thumbnail": thumbnail,
    }
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.IMAGE)
