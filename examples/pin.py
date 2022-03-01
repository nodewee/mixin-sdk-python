from mixinsdk.clients.bot_config import BotConfig
from mixinsdk.clients.http_client import (HttpClient_BotAuth,
                                          HttpClient_UserAuth)

from ._example_vars import BOT_CONFIG_FILE, USER_AUTH_TOKEN

cfg = BotConfig.from_file(BOT_CONFIG_FILE)
botclient = HttpClient_BotAuth(cfg)
userclient = HttpClient_UserAuth(USER_AUTH_TOKEN)


def test_verify_pin():
    encrypted_pin = botclient.get_encrypted_pin()
    r = botclient.api.pin.verify(encrypted_pin)
    print(r)
    assert r.get("data")


def test_get_error_logs():
    r = botclient.api.pin.get_error_logs()
    print(r)
    assert r.get("data")
