from examples._example_vars import APP_CONFIG_FILE, USER_AUTH_TOKEN
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.client_http_nosign import HttpClient_WithAccessToken
from mixinsdk.clients.config import AppConfig

cfg = AppConfig.from_file(APP_CONFIG_FILE)
appclient = HttpClient_WithAppConfig(cfg)
userclient = HttpClient_WithAccessToken(USER_AUTH_TOKEN)


def test_verify_pin():
    encrypted_pin = appclient.get_encrypted_pin()
    r = appclient.api.pin.verify(encrypted_pin)
    print(r)
    assert r.get("data")


def test_get_error_logs():
    r = appclient.api.pin.get_error_logs()
    print(r)
    assert r.get("data")
