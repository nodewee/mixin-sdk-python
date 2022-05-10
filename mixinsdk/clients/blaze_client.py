import asyncio
import gzip
import json
import logging
import signal
import sys
import time
import traceback
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import websockets

from ..constants import API_BASE_URLS
from ..utils import get_conversation_id_of_two_users
from ._sign import sign_authentication_token
from .user_config import AppConfig


class BlazeClient:
    """WebSocket client with bot config"""

    def __init__(
        self,
        config: AppConfig,
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
        self._sending_deque = deque()

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

    def run_forever(self, max_workers):
        """
        run websocket server forever
        """

        # ----- For multi-threading to handle messages
        #   Notice: websockets not support concurrent
        receiver_pool = ThreadPoolExecutor(max_workers=max_workers)
        sender_pool = ThreadPoolExecutor(max_workers=1)

        def sender():
            self.logger.debug("sender started")
            while True:
                if self._exiting:
                    break
                if not self._sending_deque:
                    time.sleep(0.1)
                    continue
                if not self.ws:
                    time.sleep(0.1)
                    continue
                raw_msg = self._sending_deque.popleft()
                try:
                    asyncio.run(self.ws.send(raw_msg))
                except Exception as e:
                    self.logger.error("Exception occurred", exc_info=True)
                    print("❌ Exception in sender:", e.__class__.__name__, str(e))
            self.logger.debug("sender stopped")

        sender_pool.submit(sender)

        # ----- For handle KeyboardInterrupt
        def sigint_handler(sig, frame):
            self._exiting = True
            self.logger.debug(" ⌨ KeyboardInterrupt is caught =====")
            self.logger.debug("Shutting down the threads ...")
            receiver_pool.shutdown(wait=True)
            sender_pool.shutdown(wait=True)
            self.logger.info("Keyboard Interrupt to Exit")
            sys.exit(0)

        signal.signal(signal.SIGINT, sigint_handler)

        asyncio.run(self._running_loop(receiver_pool, sender_pool))

    async def _running_loop(self, receiver_pool, sender_pool):
        def sync_handle_message(raw_msg):
            # For submit task to thread pool executor
            if self._exiting:
                return
            message = json.loads(gzip.decompress(raw_msg).decode())
            asyncio.run(self.on_message(message))

        def message_done_callback(future: asyncio.Future):
            error = future.exception()
            if error:
                self.on_message_error_callback(error, traceback.format_exc())

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
                    print("waiting for message...")

                    while True:
                        if self._exiting:
                            break
                        async for raw_msg in websocket:
                            if self._exiting:
                                break
                            f = receiver_pool.submit(sync_handle_message, raw_msg)
                            f.add_done_callback(message_done_callback)

            except Exception as e:
                self.logger.error("Exception occurred", exc_info=True)
                print(
                    f"❌ Exception in websocket loop: {e.__class__.__name__} : {str(e)}"
                )
            finally:
                if self._exiting:
                    break
                self.ws = None
                self.logger.warn("Will try to reconnect in 2 seconds...")
                await asyncio.sleep(2)

        receiver_pool.shutdown(wait=True)
        sender_pool.shutdown(wait=True)
        print("Blaze client stopped")
        self.logger.info("Blaze client stopped")

    def get_conversation_id_with_user(self, user_id: str):
        return get_conversation_id_of_two_users(self.config.client_id, user_id)

    async def _send_raw(self, obj) -> None:
        """Add message to sending deque"""
        if self._exiting:
            return
        raw_msg = gzip.compress(json.dumps(obj).encode())
        self._sending_deque.append(raw_msg)

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

        msg = {
            "id": str(uuid.uuid4()),
            "action": "CREATE_MESSAGE",
            "params": message,
        }
        await self._send_raw(msg)
        return
