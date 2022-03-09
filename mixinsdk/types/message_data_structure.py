import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Union

import dacite

from ..common.utils import base64_encode


class TextStruct:
    def __init__(self, text: str):
        self.text = text

    def to_base64(self) -> str:
        return base64_encode(self.text.encode("utf-8")).decode("utf-8")


class PostStruct(TextStruct):
    pass


@dataclass
class _MessageDataStructure:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_base64(self) -> str:
        return base64_encode(self.to_json().encode("utf-8")).decode("utf-8")


@dataclass
class StickerStruct(_MessageDataStructure):
    sticker_id: str
    album_id: str = None
    name: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StickerStruct":
        return dacite.from_dict(cls, data)


@dataclass
class ContactStruct(_MessageDataStructure):
    user_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContactStruct":
        return dacite.from_dict(cls, data)


@dataclass
class ButtonStruct(_MessageDataStructure):
    """
    - label: button display text
    - action: URI, mixin schema or link, e.g. 'https://mixin.one'
    - color: hex color string, e.g. '#d53120'
    """

    label: str
    action: str
    color: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ButtonStruct":
        return dacite.from_dict(cls, data)


@dataclass
class ButtonGroupStruct:
    """
    - buttons, list of ButtonStruct
    """

    buttons: Union[ButtonStruct, List[ButtonStruct]]

    def __post_init__(self):
        if isinstance(self.buttons, ButtonStruct):
            self.buttons = [self.buttons]

    def to_json(self) -> str:
        lst = []
        for btn in self.buttons:
            lst.append(btn.to_dict())
        return json.dumps(lst)

    def to_base64(self) -> str:
        return base64_encode(self.to_json().encode("utf-8")).decode("utf-8")

    @classmethod
    def from_json(cls, data: str) -> "ButtonGroupStruct":
        lst = json.loads(data)
        buttons = []
        for d in lst:
            buttons.append(ButtonStruct.from_dict(d))
        return cls(buttons=buttons)


@dataclass
class ImageStruct(_MessageDataStructure):
    """
    attachment_id: read From POST /attachments
    mime_type: e.g. "image/jpeg"
    width: int
    height: int
    size: image data bytes size
    thumbnail: "base64 encoded"
    """

    attachment_id: str
    mime_type: str
    width: int
    height: int
    size: int
    thumbnail: str

    created_at: str = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageStruct":
        return dacite.from_dict(cls, data)


# TODO more structures
