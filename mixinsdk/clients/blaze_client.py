import gzip
import json
import uuid

import websockets

from ..common.constants import CONST
from ._sign import sign_authentication_token
from .bot_config import BotConfig


class BlazeClient:
    """WebSocket client with bot config"""

    def __init__(
        self,
        config: BotConfig,
        on_message: callable,
        host_uri: str = CONST.BLAZE_HOST_DEFAULT,
    ):
        self.host_uri = host_uri
        self.config = config
        self.on_message = on_message
        self.ws = None

    def _get_auth_token(self, method: str, uri: str, bodystring: str):
        return sign_authentication_token(
            self.config.client_id,
            self.config.session_id,
            self.config.private_key,
            self.config.key_algorithm,
            method,
            uri,
            bodystring,
        )

    async def connect(self):
        if self.ws:
            return

        token = self._get_auth_token("GET", "/", "")
        headers = {"Authorization": "Bearer " + token}
        self.ws = await websockets.connect(
            self.host_uri, subprotocols=["Mixin-Blaze-1"], extra_headers=headers
        )
        print(f"Blaze client connected. (to {self.host_uri}")

    async def run(self):
        """
        run websocket server forever
        """
        while True:
            await self.connect()

            msg = {"id": str(uuid.uuid4()), "action": "LIST_PENDING_MESSAGES"}
            await self._send_raw(msg)

            while True:
                if not self.ws:
                    return
                try:
                    msg = await self.ws.recv()
                except websockets.exceptions.ConnectionClosedError:
                    self.ws = None
                    break
                except websockets.exceptions.ConnectionClosedOK:
                    return
                msg = json.loads(gzip.decompress(msg).decode())
                await self.on_message(self, msg)

    async def _send_raw(self, obj):
        return await self.ws.send(gzip.compress(json.dumps(obj).encode()))

    async def echo(self, received_msg_id):
        """
        when receive a message, must reply to server
        ACKNOWLEDGE_MESSAGE_RECEIPT ack server received message
        """
        params = {"message_id": received_msg_id, "status": "READ"}
        msg = {
            "id": str(uuid.uuid4()),
            "action": "ACKNOWLEDGE_MESSAGE_RECEIPT",
            "params": params,
        }
        return await self._send_raw(msg)

    async def send_message(self, msg_obj: dict):
        msg = {
            "id": str(uuid.uuid4()),
            "action": "CREATE_MESSAGE",
            "params": msg_obj,
        }
        return await self._send_raw(msg)
