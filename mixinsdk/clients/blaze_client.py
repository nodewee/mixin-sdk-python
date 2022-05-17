import gzip
import json
import time
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import websocket
from mixinsdk.ext import rel

from ..constants import API_BASE_URLS
from ..utils import get_conversation_id_of_two_users
from ._sign import sign_authentication_token
from .user_config import AppConfig

from . import _logging


class BlazeClient:
    """WebSocket client with bot config"""

    def __init__(
        self,
        config: AppConfig,
        on_message: callable = None,
        on_error: callable = None,
        on_close: callable = None,
        on_open: callable = None,
        api_base: str = API_BASE_URLS.BLAZE_DEFAULT,
    ):
        """
        - on_message, function, 2 argument: the_client, message:dict
        - on_error, function, 2 argument: the_client, error:Exception
        - on_open, function, 1 argument: the_client
        - on_close, function, no argument
        """
        self.config = config
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.on_open = on_open
        self.api_base = api_base

        self._exiting = False
        self._sending_deque = deque()

        self._receivers: ThreadPoolExecutor = None
        self._senders: ThreadPoolExecutor = None

    def _on_message(self, ws, raw_message):
        _logging.debug(f"Received message:\n{raw_message}")
        if not self.on_message:
            return
        message = json.loads(gzip.decompress(raw_message).decode())
        try:
            self.on_message(self, message)
        except Exception as e:
            _logging.error(f"error from on_message {e}")

    def _on_error(self, ws, error):
        if self.on_error:
            self.on_error(self, error)

    def _on_open(self, ws):
        _logging.debug("on open")
        if self.on_open:
            self.on_open(self)

    def _on_close(self):
        _logging.debug("on close")
        if self.on_close:
            self.on_close()

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

    def _send(self, msg) -> None:
        """Add message to sending deque"""
        if self._exiting:
            return
        self._sending_deque.append(msg)

    def run_forever(self, max_workers, auto_start_list_pending_message=True):
        """
        run websocket server forever
        """
        # ----- For multi-threading to handle messages
        self._receivers = ThreadPoolExecutor(max_workers=max_workers)
        #   Notice: websockets not support concurrent
        self._senders = ThreadPoolExecutor(max_workers=1)

        def sender():
            _logging.debug("Sender started")
            while True:
                if self._exiting:
                    break
                if not self._sending_deque:
                    time.sleep(0.1)
                    continue
                if not self.ws:
                    time.sleep(0.1)
                    continue
                msg = self._sending_deque.popleft()
                raw_msg = gzip.compress(json.dumps(msg).encode())
                try:
                    _logging.debug(f"sending message:\n{msg}")
                    self.ws.send(raw_msg, opcode=websocket.ABNF.OPCODE_BINARY)
                except Exception as e:
                    _logging.error("✗ Exception in sender:", exc_info=True)
                    print("✗ Exception in sender:", e.__class__.__name__, str(e))
            _logging.debug("Sender stopped")

        self._senders.submit(sender)

        # websocket.enableTrace(True)
        # create websocket connection
        auth_token = self._get_auth_token("GET", "/", "")
        self.ws = websocket.WebSocketApp(
            self.api_base,
            header={"Authorization": f"Bearer {auth_token}"},
            subprotocols=["Mixin-Blaze-1"],
            on_message=self._on_message,
            on_error=self._on_error,
            # on_close=self._on_close, # not trigger the on_close after close() connection
            on_open=self._on_open,
        )

        # Set dispatcher to automatic reconnection
        self.ws.run_forever(dispatcher=rel)
        msg = f"client id: {self.config.client_id} (name: {self.config.name})"
        _logging.info(msg)
        if auto_start_list_pending_message:
            self.start_to_list_pending_message()

        rel.signal(2, self.close)  # Keyboard Interrupt
        rel.dispatch()  # blocked

        _logging.info("blaze client stopped")
        self._on_close()

    def start_to_list_pending_message(self):
        if self._exiting:
            return
        if not self.ws:
            print("✗ Failed to listen, websocket is not connected")
            return
        msg = {"id": str(uuid.uuid4()), "action": "LIST_PENDING_MESSAGES"}
        self._send(msg)

    def close(self):
        _logging.debug("closing")
        self._exiting = True
        if self._receivers:
            self._receivers.shutdown(wait=True)
        if self._senders:
            self._senders.shutdown(wait=True)
        try:
            self.ws.close()
        except Exception:
            pass
        rel.abort()
        self.ws = None

    def get_conversation_id_with_user(self, user_id: str):
        return get_conversation_id_of_two_users(self.config.client_id, user_id)

    def echo(self, received_msg_id):
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
        return self._send(msg)

    def send_message(self, message: dict):
        """
        - message, use types.message.pack_message() to make it
        """

        msg = {
            "id": str(uuid.uuid4()),
            "action": "CREATE_MESSAGE",
            "params": message,
        }
        return self._send(msg)
