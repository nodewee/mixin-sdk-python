from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data
import time


def use_logging():
    import logging
    from logging.handlers import RotatingFileHandler

    log_handler = RotatingFileHandler(
        "bot.log",
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    log_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    log_handler.setLevel(logging.INFO)
    logger = logging.getLogger("root")
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)


class MixinBotClient:
    def __init__(self):
        self.blaze: BlazeClient = None
        self.http: HttpClient_AppAuth = None


def handle_error(client, error):
    print(f"✗ Error: {error}")


def on_open(client: BlazeClient):
    print(f"Blaze client opened. client id: {client.config.client_id}")


def on_close():
    print("Blaze client closed")


def handle_message(blaze: BlazeClient, message):
    global bot
    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # mixin blaze server received the message
        return

    if action == "LIST_PENDING_MESSAGES":
        print("Mixin blaze server: 👂")
        return

    if action == "ERROR":
        print("Received error message:", message["error"])
        return
        """example message={
            "id": "00000000-0000-0000-0000-000000000000",
            "action": "ERROR",
            "error": {
                "status": 202,
                "code": 400,
                "description": "The request body can't be parsed as valid data.",
            },
        }"""

    if action == "CREATE_MESSAGE":
        error = message.get("error")
        if error:
            print(error)
            return

        data = message["data"]
        msgview = MessageView.from_dict(data)

        if msgview.conversation_id == "":
            # is response status of send message, ignore
            return

        if msgview.type == "message":
            print(f"message from: {msgview.user_id}")

            if msgview.data_decoded == "hi":
                blaze.send_message(
                    pack_message(pack_text_data("👋 hello"), msgview.conversation_id),
                )
            elif msgview.data_decoded == "stop":
                blaze.echo(msgview.message_id)
                time.sleep(1.5)  # wait for sended echo message
                blaze.close()

            blaze.echo(msgview.message_id)
            return


use_logging()
bot_config = AppConfig.from_file("./data/bot-config-test.json")
bot = MixinBotClient()
bot.http = HttpClient_AppAuth(bot_config)
bot.blaze = BlazeClient(
    bot_config,
    on_message=handle_message,
    on_error=handle_error,
    on_close=on_close,
    on_open=on_open,
)


bot.blaze.run_forever(2)
