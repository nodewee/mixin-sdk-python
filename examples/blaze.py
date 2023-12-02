"""blaze client example"""

import json
import logging

from examples._example_vars import APP_CONFIG_FILE
from mixinsdk.clients.client_blaze import BlazeClient
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.config import AppConfig
from mixinsdk.types.message import pack_message, pack_text_data

logger = logging.getLogger("blaze")
logger.setLevel(logging.INFO)
stream_logger = logging.StreamHandler()
stream_logger.setLevel(logging.INFO)
logger.addHandler(stream_logger)


def message_handle_error_callback(error, details):
    """message_handle_error_callback"""
    logger.error("===== error_callback =====")
    logger.error("error: %s", error)
    logger.error("details: %s", details)


def message_handle(bot, message):
    """message_handle"""
    action = message["action"]

    if action == "ERROR":
        logger.warning(message["error"])

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        logger.info(str(error))
        return

    logger.info("%s", json.dumps(message, indent=4, ensure_ascii=False))

    msg_data = message.get("data", {})
    data = msg_data.get("data")
    category = msg_data.get("category")

    raw_data = json.dumps(data, indent=4, ensure_ascii=False)
    parsed_data = json.dumps(
        bot.parse_message_data(data, category), indent=4, ensure_ascii=False
    )

    reply_text = f'Hi,user {msg_data.get("user_id")}\nI had received your {category} message\n\n{raw_data}\n\nparsed data:\n{parsed_data}'

    #
    # encrypted = bot.encrypt_message_data(base64.b64decode(reply_text).encode())
    bot.xin.api.send_messages(
        pack_message(
            pack_text_data(reply_text),
            conversation_id=msg_data.get("conversation_id"),
            quote_message_id=msg_data.get("message_id"),
        )
    )
    bot.echo(msg_data.get("message_id"))
    return


config = AppConfig.from_file(APP_CONFIG_FILE)
bot = BlazeClient(
    config,
    on_message=message_handle,
    on_error=message_handle_error_callback,
)
bot.xin = HttpClient_WithAppConfig(config)
bot.run_forever(2)
