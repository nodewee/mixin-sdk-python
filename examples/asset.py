from examples._example_vars import APP_CONFIG_FILE
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.config import AppConfig

cfg = AppConfig.from_file(APP_CONFIG_FILE)
appclient = HttpClient_WithAppConfig(cfg)


def test_list_assets():
    r = appclient.api.asset.get_assets_list()
    print(r)
    assert r["data"] is not None


def test_get_fiat_exchange_rates():
    r = appclient.api.asset.get_fiat_exchange_rates()
    print(r)
    assert r["data"] is not None
