from io import FileIO
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

    def create_attachment(self) -> dict:
        """After creating action, then upload the attachment to upload_url,
        and then the attachment_id can be used sending images,
        videos, files and other messages.
        """
        payload = {"attachment_id": "", "upload_url": "", "view_url": ""}
        return self._http.post("/attachments", payload)

    def read_attachment(self, attachment_id: str):
        """get a specific attachment metadata"""
        return self._http.get(f"/attachments/{attachment_id}")

    def upload_attachment(self, upload_url: str, file: Union[FileIO, bytes]):
        """use create_attachment() to get upload_url"""
        import httpx

        headers = {}
        headers["Content-Type"] = "application/octet-stream"
        headers["x-amz-acl"] = "public-read"

        return httpx.put(upload_url, data=file, headers=headers)
