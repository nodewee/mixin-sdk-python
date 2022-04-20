import base64
import decimal
import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict

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


def pack_message(
    conversation_id: str,
    category: str,
    data: str,
    message_id: str = None,
    recipient_id: str = None,
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
        "category": category,
        "data": data,
        "message_id": message_id,
    }
    if recipient_id:
        pld["recipient_id"] = recipient_id
    if representative_id:
        pld["representative_id"] = representative_id
    if quote_message_id:
        pld["quote_message_id"] = quote_message_id

    return pld


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
        self.data_decoded = parse_data(self.data, self.category)
        self.created_at = parse_rfc3339_to_datetime(self.created_at)
        self.updated_at = parse_rfc3339_to_datetime(self.updated_at)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageView":
        return dacite.from_dict(cls, data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_data(data_str: str, category: str):
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
