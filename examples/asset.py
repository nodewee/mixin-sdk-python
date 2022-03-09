from mixinsdk.clients.bot_config import BotConfig
from mixinsdk.clients.http_client import HttpClient_BotAuth, HttpClient_UserAuth

from ._example_vars import BOT_CONFIG_FILE, USER_AUTH_TOKEN

cfg = BotConfig.from_file(BOT_CONFIG_FILE)
botclient = HttpClient_BotAuth(cfg)
userclient = HttpClient_UserAuth(USER_AUTH_TOKEN)


def test_list_assets():
    r = botclient.api.asset.get_assets_list()
    print(r)
    assert r["data"] is not None


def test_get_fiat_exchange_rates():
    r = botclient.api.asset.get_fiat_exchange_rates()
    print(r)
    assert r["data"] is not None
