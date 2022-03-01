import asyncio

from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth

from ._example_vars import BOT_CONFIG_FILE, MY_USER_ID

cfg = BotConfig.from_file(BOT_CONFIG_FILE)
bot = HttpClient_BotAuth(cfg)


def _get_conv_id_with_user(user_id):
    return bot.api.conversation.get_unique_id(cfg.client_id, user_id)


async def _async_call(func, *args, **kwargs):
    return func(*args, **kwargs)


async def send_text_message():
    return await _async_call(
        bot.api.message.send_text, _get_conv_id_with_user(MY_USER_ID), "Hello async"
    )


def run():
    asyncio.run(send_text_message())
