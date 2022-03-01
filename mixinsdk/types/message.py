import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict

import dacite

from ..common.utils import base64_decode, parse_rfc3339_to_datetime
from .message_data_structure import (ButtonStruct, ContactStruct, ImageStruct,
                                     PostStruct, StickerStruct, TextStruct)


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


@dataclass
class MessageRequest:
    """
    - conversation_id, *required*
    - category, *required*
    - data, *required*, Base64 encoded string
    - recipient_id, optional when send single message,
        *required* when send list of messages
    - message_id, optional, if not set, will be generated randomly
    """

    conversation_id: str
    category: str
    data: str
    recipient_id: str = None
    message_id: str = None
    representative_id: str = None
    quote_message_id: str = None

    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageRequest":
        return dacite.from_dict(cls, data)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for k, v in asdict(self).items():
            # removed empty items
            if v is not None:
                d[k] = v
        return d


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
        self.data_decoded, self.data_struct = parse_data(self.data, self.category)
        self.created_at = parse_rfc3339_to_datetime(self.created_at)
        self.updated_at = parse_rfc3339_to_datetime(self.updated_at)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageView":
        return dacite.from_dict(cls, data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_data(data: str, category: str) -> object:
    """
    parse message data (Base64 encoded string) to specific message data structure object

    Returns: (data_decoded, data_struct)
    """
    d = base64_decode(data).decode("utf-8")
    data_decoded = d
    if category == MESSAGE_CATEGORIES.TEXT:
        return data_decoded, TextStruct(d)
    if category == MESSAGE_CATEGORIES.POST:
        return data_decoded, PostStruct(d)

    try:
        d = json.loads(d)
        print(f"msg data struct: {d}")
    except json.JSONDecodeError:
        print(f"Failed to json decode data: {d}")
    data_decoded = d

    if category == MESSAGE_CATEGORIES.STICKER:
        return data_decoded, StickerStruct(**d)
    if category == MESSAGE_CATEGORIES.CONTACT:
        return data_decoded, ContactStruct(**d)
    if category == MESSAGE_CATEGORIES.IMAGE:
        return data_decoded, ImageStruct(**d)
    if category == MESSAGE_CATEGORIES.BUTTON_GROUP:
        buttons = []
        for i in d:
            buttons.append(ButtonStruct(**i))

    return data_decoded, f"Unknown message category: {category}"
