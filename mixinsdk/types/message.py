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
    PLAIN_TEXT: str = "PLAIN_TEXT"
    ENCRYPTED_TEXT: str = "ENCRYPTED_TEXT"

    PLAIN_POST: str = "PLAIN_POST"
    ENCRYPTED_POST: str = "ENCRYPTED_POST"

    PLAIN_STICKER: str = "PLAIN_STICKER"
    ENCRYPTED_STICKER: str = "ENCRYPTED_STICKER"

    PLAIN_CONTACT: str = "PLAIN_CONTACT"
    ENCRYPTED_CONTACT: str = "ENCRYPTED_CONTACT"

    PLAIN_IMAGE: str = "PLAIN_IMAGE"
    ENCRYPTED_IMAGE: str = "ENCRYPTED_IMAGE"

    PLAIN_VIDEO: str = "PLAIN_VIDEO"
    ENCRYPTED_VIDEO: str = "ENCRYPTED_VIDEO"

    PLAIN_FILE: str = "PLAIN_DATA"
    ENCRYPTED_FILE: str = "ENCRYPTED_DATA"

    PLAIN_AUDIO: str = "PLAIN_AUDIO"
    ENCRYPTED_AUDIO: str = "ENCRYPTED_AUDIO"

    PLAIN_LIVE: str = "PLAIN_LIVE"
    PLAIN_LOCATION: str = "PLAIN_LOCATION"

    APP_CARD: str = "APP_CARD"
    BUTTON_GROUP: str = "APP_BUTTON_GROUP"

    SYSTEM_ACCOUNT_SNAPSHOT: str = "SYSTEM_ACCOUNT_SNAPSHOT"
    SYSTEM_CONVERSATION: str = "SYSTEM_CONVERSATION"
    TRANSCRIPT: str = "TRANSCRIPT"  # ?

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
        self.data_parsed = None
        self.created_at = parse_rfc3339_to_datetime(self.created_at)
        self.updated_at = parse_rfc3339_to_datetime(self.updated_at)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageView":
        return dacite.from_dict(cls, data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    encrypt_func: callable = None,
):
    """
    - conversation_id, *required*
    - category, *required*
    - data, *required*, base64 encoded string of content payload
    - recipient_id, *recommended*,
        *required* when send encrypted message or list of messages
    - message_id, optional, if not set, will be generated randomly
    """

    message_id = message_id if message_id else str(uuid.uuid4())

    pld = {
        "conversation_id": conversation_id,
        "message_id": message_id,
    }

    if not encrypt_func:
        pld["category"] = data_obj.category
        pld["data_base64"] = data_obj.b64encoded_data

    else:  # encrypt message data
        if not recipient_id:
            raise ValueError("recipient_id is required for encrypted message")
        pld["category"] = data_obj.category.replace("PLAIN_", "ENCRYPTED_")

        encrypted_data, recipient_sessions, checksum = encrypt_func(
            data_obj.b64encoded_data, conversation_id
        )
        pld["data"] = ""
        pld["data_base64"] = encrypted_data
        pld["recipient_sessions"] = recipient_sessions
        pld["checksum"] = checksum

    if recipient_id:
        pld["recipient_id"] = recipient_id
    if representative_id:
        pld["representative_id"] = representative_id
    if quote_message_id:
        pld["quote_message_id"] = quote_message_id

    return pld


def pack_text_data(text) -> MessageDataObject:
    payload = text
    data_b64_str = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    cat = MESSAGE_CATEGORIES.PLAIN_TEXT
    return MessageDataObject(payload, data_b64_str, cat)


def pack_post_data(markdown_text) -> MessageDataObject:
    payload = markdown_text
    data_b64_str = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    cat = MESSAGE_CATEGORIES.PLAIN_POST

    return MessageDataObject(payload, data_b64_str, cat)


def pack_sticker_data(sticker_id, album_id=None, name=None) -> MessageDataObject:
    payload = {"sticker_id": sticker_id}
    if album_id:
        payload["album_id"] = album_id
    if name:
        payload["name"] = name
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_STICKER)


def pack_contact_data(user_id) -> MessageDataObject:
    payload = {"user_id": user_id}
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_CONTACT)


def pack_button(label, action, color) -> dict:
    """
    Args:
    - label: button display text
    - action: URI, mixin schema or link, e.g. 'https://mixin.one'
    - color: hex color string, e.g. 'd53120'

    Return:
        payload:dict
    """

    if not color.startswith("#"):
        color = "#" + color
    payload = {"label": label, "action": action, "color": color}
    return payload


def pack_button_group_data(buttons: Union[Dict, List[Dict]]) -> MessageDataObject:
    """
    Args:
        - buttons, list of button payload. maximum 6 buttons
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
    width: int,
    height: int,
    thumbnail: str,
):
    """
    Args:
        attachment_id: "read From POST /attachments"
        mime_type: e.g. "image/jpeg"
        size: image data bytes size
        thumbnail: "base64 encoded"
    """
    payload = {
        "attachment_id": attachment_id,
        "mime_type": mime_type,
        "size": size,
        "width": width,
        "height": height,
        "thumbnail": thumbnail,
    }

    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_IMAGE)


def pack_video_data(
    attachment_id: str,
    mime_type: str,
    size: int,
    width: int,
    height: int,
    duration: int,
    thumbnail: str = None,
    created_at: str = None,
):
    """
    Args:
        attachment_id: "Read From POST /attachments"
        mime_type: e.g. "video/mp4"
        thumbnail: "base64 encoded"
        created_at: "e.g. 2022-09-18T08:04:04.073818923Z"
    """
    payload = {
        "attachment_id": attachment_id,
        "mime_type": mime_type,
        "width": width,
        "height": height,
        "size": size,
        "duration": duration,
    }
    if thumbnail:
        payload["thumbnail"] = thumbnail
    if created_at:
        payload["created_at"] = created_at
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_VIDEO)


def pack_audio_data(
    attachment_id: str,
    mime_type: str,
    size: int,
    duration: int,
    waveform: str,
    created_at: str = None,
):
    """
    Args:
        attachment_id: "Read From POST /attachments"
        mime_type: e.g. "audio/ogg"
        waveform: "audio waveform"
        created_at: "e.g. 2022-09-18T08:04:04.073818923Z"
    """
    payload = {
        "attachment_id": attachment_id,
        "mime_type": mime_type,
        "size": size,
        "duration": duration,
        "waveform": waveform,
    }
    if created_at:
        payload["created_at"] = created_at
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_AUDIO)


def pack_file_data(
    attachment_id: str,
    mime_type: str,
    size: int,
    name: str,
):
    """
    Args:
        attachment_id: "Read From POST /attachments"
        mime_type: e.g. "application/pdf",
        "size": 1024
        "name": "example.pdf"
    """
    payload = {
        "attachment_id": attachment_id,
        "mime_type": mime_type,
        "size": size,
        "name": name,
    }
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_FILE)


def pack_livecard_data(
    url: str, thumb_url: str, width: int, height: int, shareable: bool = True
):
    """
    Args:
        "url": "e.g. https://mixin.one/live.m3u8"
        "thumb_url": "e.g. https://mixin.one/logo.png"
    """
    payload = {
        "url": url,
        "thumb_url": thumb_url,
        "width": width,
        "height": height,
        "shareable": shareable,
    }
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.PLAIN_LIVE)


def pack_appcard_data(
    app_id: str,
    icon_url: str,
    action: str,
    title: str,
    description: str = "",
    shareable: bool = True,
):
    """
    Args:
        "app_id": "e.g. 7404c815-0393-4ea3-b9f2-b08efe4c72da"
        "icon_url": "e.g. https://mixin.one/assets/98b586edb270556d1972112bd7985e9e.png"
        "action": "e.g. https://mixin.one"
        "title": "e.g. Mixin" // 1 <= size(title) <= 36
        "description": "e.g. Hello World." // 1 <= size(description) <= 128
    """
    payload = {
        "app_id": app_id,
        "icon_url": icon_url,
        "action": action,
        "title": title,
        "description": description,
        "shareable": shareable,
    }
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return MessageDataObject(payload, b64encoded_data, MESSAGE_CATEGORIES.APP_CARD)
