import asyncio
import gzip
import json
import signal
import sys
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

        self._exiting = False

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

    async def run_forever(self, max_workers):
        """
        run websocket server forever
        """

        # ----- For multi-threading to handle messages
        executors = ThreadPoolExecutor(max_workers=max_workers)

        def sync_handle_message(raw_msg):
            # For submit task to thread pool executor
            if self._exiting:
                return
            message = json.loads(gzip.decompress(raw_msg).decode())
            asyncio.run(flow_control(message))

        def message_done_callback(future: asyncio.Future):
            error = future.exception()
            if error:
                self.on_message_error_callback(error, traceback.format_exc())

        # ----- For solved problem:
        #       Asyncio Fatal Error on SSL Transport - IndexError Deque Index Out Of Range
        async def waiter(event, message):
            await event.wait()
            await self.on_message(message)

        async def flow_control(message):
            event = asyncio.Event()
            waiter_task = asyncio.create_task(waiter(event, message))
            await asyncio.sleep(0.5)
            event.set()
            # Wait until the waiter task is finished.
            await waiter_task

        # ----- For handle KeyboardInterrupt
        def sigint_handler(sig, frame):
            self._exiting = True
            print(" ⌨ KeyboardInterrupt is caught =====")
            print("Shutting down the threads ...")
            executors.shutdown(wait=True)
            print("Exit")
            sys.exit(0)

        signal.signal(signal.SIGINT, sigint_handler)

        # ----- Run websocket server forever
        while True:
            if self._exiting:
                break
            try:
                # connect to server
                auth_token = self._get_auth_token("GET", "/", "")
                async with websockets.connect(
                    self.api_base,
                    subprotocols=["Mixin-Blaze-1"],
                    extra_headers={"Authorization": f"Bearer {auth_token}"},
                ) as websocket:
                    print("Connected")
                    self.ws = websocket

                    msg = {"id": str(uuid.uuid4()), "action": "LIST_PENDING_MESSAGES"}
                    await self._send_raw(msg)
                    print("waiting for message...")

                    while True:
                        if self._exiting:
                            break
                        async for raw_msg in websocket:
                            if self._exiting:
                                break
                            f = executors.submit(sync_handle_message, raw_msg)
                            f.add_done_callback(message_done_callback)
                self.ws = None
                print("Connection closed")
            except websockets.exceptions.ConnectionClosedError:
                # reconnect automatically on errors
                self.ws = None
                print("Connection closed error. try to reconnect")
                continue
            except websockets.ConnectionClosed:
                # reconnect automatically on errors
                self.ws = None
                print("Connection closed. to reconnect")
                continue
            except Exception as e:
                self.ws = None
                print("-" * 30)
                print(traceback.format_exc())
                print(str(e))
                print("-" * 30)
                break  # stop the client

        executors.shutdown(wait=True)
        print("Blaze client stopped")

    def get_conversation_id_with_user(self, user_id: str):
        return get_conversation_id_of_two_users(self.config.client_id, user_id)

    async def _send_raw(self, obj):
        if self._exiting:
            return
        if not self.ws:
            raise Exception("websocket not connected")
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
        msg_data_obj,
        conversation_id,
        message_id=None,
        recipient_id=None,
        quote_message_id=None,
    ):

        # recipient_id = to_user_id
        msg = pack_message(
            msg_data_obj,
            conversation_id,
            recipient_id,
            message_id,
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
