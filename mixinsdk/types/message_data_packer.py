import base64
import json
from typing import Dict, List, Union

from .message import MESSAGE_CATEGORIES


def pack_text(text):
    """return payload, b64encoded_data, category"""
    payload = text
    b64encoded_data = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    category = MESSAGE_CATEGORIES.TEXT
    return payload, b64encoded_data, category


def pack_post(markdown_text):
    """return payload, b64encoded_data, category"""
    payload = markdown_text
    b64encoded_data = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    category = MESSAGE_CATEGORIES.POST
    return payload, b64encoded_data, category


def pack_sticker(sticker_id, album_id=None, name=None):
    """return payload, b64encoded_data, category"""
    payload = {"sticker_id": sticker_id}
    if album_id:
        payload["album_id"] = album_id
    if name:
        payload["name"] = name
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    category = MESSAGE_CATEGORIES.STICKER
    return payload, b64encoded_data, category


def pack_contact(user_id):
    """return payload, b64encoded_data, category"""
    payload = {"user_id": user_id}
    b64encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
    category = MESSAGE_CATEGORIES.CONTACT
    return payload, b64encoded_data, category


def pack_button(label, action, color):
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


def pack_button_group(buttons: Union[Dict, List[Dict]]):
    """
    Args:
        - buttons, list of button payload

    Return (payload, b64encoded_data, category)
    """
    if isinstance(buttons, Dict):
        buttons = [buttons]
    payload = buttons
    b64encode_data = base64.b64encode(json.dumps(payload).encode()).decode()
    category = MESSAGE_CATEGORIES.BUTTON_GROUP
    return payload, b64encode_data, category


def pack_image(
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
    b64encode_data = base64.b64encode(json.dumps(payload).encode()).decode()
    category = MESSAGE_CATEGORIES.IMAGE
    return payload, b64encode_data, category
