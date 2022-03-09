from typing import Dict, List, Union

from ..clients._requests import HttpRequest
from ..types.message import MESSAGE_CATEGORIES, MessageRequest
from ..types.message_data_structure import (
    ButtonGroupStruct,
    ButtonStruct,
    ContactStruct,
    PostStruct,
    StickerStruct,
    TextStruct,
)


class MessageApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    def send_messages(self, messages: Union[List[dict], dict]):
        """
        messages: single message object or list of message objects.
            if send multiple messages, every message must contain recipient_id
        A maximum of 100 messages can be sent in batch each time, and the message body cannot exceed 128Kb.
        """

        return self._http.post("/messages", messages)

    def send_text(
        self,
        conversation_id: str,
        text: str,
        recipient_id: str = None,
        message_id: str = None,
        representative_id: str = None,
        quote_message_id: str = None,
    ):
        msg = MessageRequest(
            conversation_id,
            MESSAGE_CATEGORIES.TEXT,
            TextStruct(text).to_base64(),
            recipient_id,
            message_id,
            representative_id,
            quote_message_id,
        ).to_dict()
        return self.send_messages(msg)

    def send_post(
        self,
        conversation_id: str,
        text: str,
        recipient_id: str = None,
        message_id: str = None,
        representative_id: str = None,
        quote_message_id: str = None,
    ):
        msg = MessageRequest(
            conversation_id,
            MESSAGE_CATEGORIES.POST,
            PostStruct(text).to_base64(),
            recipient_id,
            message_id,
            representative_id,
            quote_message_id,
        ).to_dict()
        return self.send_messages(msg)

    def send_sticker(
        self,
        conversation_id: str,
        sticker_id: str,
        recipient_id: str = None,
        message_id: str = None,
        representative_id: str = None,
        quote_message_id: str = None,
    ):
        data = StickerStruct(sticker_id).to_base64()
        msg = MessageRequest(
            conversation_id,
            MESSAGE_CATEGORIES.STICKER,
            data,
            recipient_id,
            message_id,
            representative_id,
            quote_message_id,
        ).to_dict()
        return self.send_messages(msg)

    def send_contact(
        self,
        conversation_id: str,
        contact_user_id: str,
        recipient_id: str = None,
        message_id: str = None,
        representative_id: str = None,
        quote_message_id: str = None,
    ):
        data = ContactStruct(contact_user_id).to_base64()
        msg = MessageRequest(
            conversation_id,
            MESSAGE_CATEGORIES.CONTACT,
            data,
            recipient_id,
            message_id,
            representative_id,
            quote_message_id,
        ).to_dict()
        return self.send_messages(msg)

    def send_button(
        self,
        conversation_id: str,
        label: str,
        action: str,
        color: str,
        recipient_id: str = None,
        message_id: str = None,
        representative_id: str = None,
        quote_message_id: str = None,
    ):
        data = ButtonGroupStruct(ButtonStruct(label, action, color)).to_base64()
        msg = MessageRequest(
            conversation_id,
            MESSAGE_CATEGORIES.BUTTON_GROUP,
            data,
            recipient_id,
            message_id,
            representative_id,
            quote_message_id,
        ).to_dict()
        return self.send_messages(msg)

    def send_button_group(
        self,
        conversation_id: str,
        buttons: List[ButtonStruct],
        recipient_id: str = None,
        message_id: str = None,
        representative_id: str = None,
        quote_message_id: str = None,
    ):
        data = ButtonGroupStruct(buttons).to_base64()
        msg = MessageRequest(
            conversation_id,
            MESSAGE_CATEGORIES.BUTTON_GROUP,
            data,
            recipient_id,
            message_id,
            representative_id,
            quote_message_id,
        ).to_dict()
        return self.send_messages(msg)
