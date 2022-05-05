import asyncio
import gzip
import json
import logging
import signal
import sys
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

import websockets

from ..constants import API_BASE_URLS
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
        logger: logging.Logger = None,
        api_base: str = API_BASE_URLS.BLAZE_DEFAULT,
    ):
        """
        - on_message argument: message:dict
        - on_message_error_callback arguments: error:object, traceback_details:string
        """
        self.config = config
        self.on_message = on_message
        self.on_message_error_callback = on_message_error_callback
        self.logger = logger if logger else logging.getLogger("blaze client")
        self.api_base = api_base

        self.ws = None
        self._exiting = False

        msg = f"bot id: {self.config.client_id}\n\tname: {self.config.name}"
        self.logger.info(msg)
        print(msg)

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
        #   Asyncio Fatal Error on SSL Transport -
        #   IndexError Deque Index Out Of Range
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
            self.logger.debug(" ⌨ KeyboardInterrupt is caught =====")
            self.logger.debug("Shutting down the threads ...")
            executors.shutdown(wait=True)
            self.logger.info("KeyboardInterrupt to Exit")
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
                    self.logger.info("Connected")
                    self.ws = websocket

                    msg = {"id": str(uuid.uuid4()), "action": "LIST_PENDING_MESSAGES"}
                    await self._send_raw(msg)
                    self.logger.info("waiting for message...")

                    while True:
                        if self._exiting:
                            break
                        async for raw_msg in websocket:
                            if self._exiting:
                                break
                            f = executors.submit(sync_handle_message, raw_msg)
                            f.add_done_callback(message_done_callback)
                self.ws = None
                self.logger.warn("Connection closed")
            except websockets.exceptions.ConnectionClosedError:
                # reconnect automatically on errors
                self.ws = None
                self.logger.error(
                    "Connection closed error. try to reconnect.", exc_info=True
                )
                await asyncio.sleep(2)
                continue
            except websockets.ConnectionClosed:
                # reconnect automatically on errors
                self.ws = None
                self.logger.warn("Connection closed. to reconnect.", exc_info=True)
                await asyncio.sleep(2)
                continue
            except Exception as e:
                self.ws = None
                print(f"❌ Exception: {str(e)}")
                self.logger.error("Exception occurred. stop the client", exc_info=True)
                break  # stop the client

        executors.shutdown(wait=True)
        self.logger.info("Blaze client stopped")

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

    async def send_message(self, message: dict):
        """
        - message, use types.message.pack_message() to make it
        """

        raw_msg = {
            "id": str(uuid.uuid4()),
            "action": "CREATE_MESSAGE",
            "params": message,
        }
        await self._send_raw(raw_msg)
        return
