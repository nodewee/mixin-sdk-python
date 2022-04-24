from typing import List, Union

from ..clients._requests import HttpRequest


class MessageApi:
    def __init__(self, http: HttpRequest):
        self._http = http

    def send_messages(self, messages: Union[List[dict], dict]):
        """
        Args:
        - messages: single message object(dict) or list of message objects.\n
            If send multiple messages, every message must contain recipient_id.\n
            A maximum of 100 messages can be sent in batch each time,
            and the message body cannot exceed 128Kb.
        """

        return self._http.post("/messages", messages)
