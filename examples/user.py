from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.client_http_nosign import HttpClient_WithAccessToken
from mixinsdk.clients.config import AppConfig

from ._example_vars import APP_CONFIG_FILE, MY_USER_ID, USER_AUTH_TOKEN

cfg = AppConfig.from_file(APP_CONFIG_FILE)
appclient = HttpClient_WithAppConfig(cfg)
userclient = HttpClient_WithAccessToken(USER_AUTH_TOKEN)


# Read self profile with User's oauth access token
def test_read_me_of_user():
    r = userclient.api.user.get_me()
    print(r)
    assert r["data"]


# Read self profile of Bot
def test_read_me_of_bot():
    r = appclient.api.user.get_me()
    print(r)
    assert r["data"]


def test_read_user():
    # Team Mixin
    r = appclient.api.user.get_user("773e5e77-4107-45c2-b648-8fc722ed77f5")
    # r = appclient.api.user.get_user(MY_USER_ID)
    print(r)
    assert r["data"]


# Read multiple users
def test_read_users():
    uid_list = [MY_USER_ID, appclient.config.client_id]
    r = appclient.api.user.get_users(uid_list)
    print(r)
    assert r["data"]


def test_search_user():
    r = appclient.api.user.search_user("37297553")
    print(r)
    assert r["data"]


def test_get_friends():
    r = appclient.api.user.get_friends()
    # r = userclient.api.user.get_friends()
    print(r)
    assert r["data"] is not None


def test_get_blocking_users():
    r = appclient.api.user.get_blocking_users()
    print(r)
    assert r["data"] is not None


def test_create_network_user():
    r = appclient.api.user.create_network_user()
    print(r)
    assert r["data"] is not None
