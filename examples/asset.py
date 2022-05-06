from mixinsdk.clients.user_config import AppConfig
from mixinsdk.clients.http_client import HttpClient_AppAuth

from ._example_vars import BOT_CONFIG_FILE

cfg = AppConfig.from_file(BOT_CONFIG_FILE)
botclient = HttpClient_AppAuth(cfg)


def test_list_assets():
    r = botclient.api.asset.get_assets_list()
    print(r)
    assert r["data"] is not None


def test_get_fiat_exchange_rates():
    r = botclient.api.asset.get_fiat_exchange_rates()
    print(r)
    assert r["data"] is not None
