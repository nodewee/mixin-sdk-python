import asyncio
import gzip
import json
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

import websockets

from ..constants import API_BASE_URLS
from ..types.message import pack_message
from ..utils import get_conversation_id_of_two_users
from ._sign import sign_authentication_token
from .bot_config import BotConfig


class BlazeClient:
    """WebSocket client with bot config"""

    def __init__(
        self,
        config: BotConfig,
        on_message: callable,
        on_message_error_callback: callable = None,
        api_base: str = API_BASE_URLS.BLAZE_DEFAULT,
    ):
        """
        - on_message argument: message:dict
        - on_message_error_callback arguments: error:object, traceback_details:string
        """
        self.api_base = api_base
        self.config = config
        self.on_message = on_message
        self.on_message_error_callback = on_message_error_callback
        self.ws = None

        print(f"bot id: {self.config.client_id}")
        print(f"\tname: {self.config.name}")

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
            self.api_base, subprotocols=["Mixin-Blaze-1"], extra_headers=headers
        )
        print(f"Blaze client connected. (to {self.api_base}")

    async def run_forever(self, max_workers):
        """
        run websocket server forever
        """

        executors = ThreadPoolExecutor(max_workers=max_workers)

        def sync_handle_message(raw_msg):
            # print("handle new message")
            message = json.loads(gzip.decompress(raw_msg).decode())
            asyncio.run(self.on_message(message))

        def message_done_callback(future: asyncio.Future):
            error = future.exception()
            if error:
                self.on_message_error_callback(error, traceback.format_exc())

        while True:
            await self.connect()

            msg = {"id": str(uuid.uuid4()), "action": "LIST_PENDING_MESSAGES"}
            await self._send_raw(msg)
            print("waiting for message...")

            while True:
                if not self.ws:
                    return

                try:
                    raw_msg = await self.ws.recv()
                except websockets.exceptions.ConnectionClosedError:
                    self.ws = None
                    break
                except websockets.exceptions.ConnectionClosedOK:
                    self.ws = None
                    break

                f = executors.submit(sync_handle_message, raw_msg)
                f.add_done_callback(message_done_callback)

    def get_conversation_id_with_user(self, user_id: str):
        return get_conversation_id_of_two_users(self.config.client_id, user_id)

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

    async def send_message(
        self,
        msg_b64encoded_data,
        msg_category,
        conversation_id,
        message_id=None,
        recipient_id=None,
        quote_message_id=None,
    ):
        # if not (to_user_id or to_group_id):
        #     raise ValueError("to_user_id or to_group_id must be specified")
        # if to_user_id:
        #     conv_id = self.get_conversation_id_with_user(to_user_id)
        # else:
        #     conv_id = to_group_id

        # recipient_id = to_user_id
        msg = pack_message(
            conversation_id,
            msg_category,
            msg_b64encoded_data,
            message_id,
            recipient_id,
            None,  # representative_id
            quote_message_id,
        )

        raw_msg = {
            "id": str(uuid.uuid4()),
            "action": "CREATE_MESSAGE",
            "params": msg,
        }
        await self._send_raw(raw_msg)
        return
