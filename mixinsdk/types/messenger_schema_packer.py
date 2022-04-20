import decimal
import json
import urllib.parse
import uuid
from base64 import b64encode
from dataclasses import dataclass
from typing import Union


def generate_sharing_uri(category: str, data: str, conversation_id: str = None) -> str:
    """
    params:
    - data: Base64 encoded string
    """
    uri = f"mixin://send?category={category}&data={data}"
    if conversation_id:
        uri += f"&conversation_id={conversation_id}"
    return uri


@dataclass
class SharingTextStruct:
    text: str
    conversation_id: str = None

    def to_uri(self):
        data = b64encode(self.text.encode("utf-8")).decode("utf-8")
        return generate_sharing_uri("text", data, self.conversation_id)


@dataclass
class SharingImageStruct:
    image_url: str
    conversation_id: str = None

    def to_uri(self):
        payload = {"url": self.image_url}
        data = b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        return generate_sharing_uri("image", data, self.conversation_id)


# TODO: more sharing schema types


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
    uri = f"mixin://pay?recipient={recipient_id}&asset={asset_id}&amount={amount}&trace={trace_id}"
    if memo:
        uri += f"&memo={urllib.parse.quote(memo)}"
    return uri


# TODO: more payment schema types


# TODO: other schema types
