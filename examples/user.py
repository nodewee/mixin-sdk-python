from mixinsdk.clients.user_config import AppConfig
from mixinsdk.clients.http_client import HttpClient_AppAuth, HttpClient_UserOAuth

from ._example_vars import BOT_CONFIG_FILE, MY_USER_ID, USER_AUTH_TOKEN

cfg = AppConfig.from_file(BOT_CONFIG_FILE)
botclient = HttpClient_AppAuth(cfg)
userclient = HttpClient_UserOAuth(USER_AUTH_TOKEN)


# Read self profile with User's oauth access token
def test_read_me_of_user():
    r = userclient.api.user.get_me()
    print(r)
    assert r["data"]


# Read self profile of Bot
def test_read_me_of_bot():
    r = botclient.api.user.get_me()
    print(r)
    assert r["data"]


def test_read_user():
    r = botclient.api.user.get_user(MY_USER_ID)
    print(r)
    assert r["data"]


# Read multiple users
def test_read_users():
    uid_list = [MY_USER_ID, botclient.config.client_id]
    r = botclient.api.user.get_users(uid_list)
    print(r)
    assert r["data"]


def test_search_user():
    r = botclient.api.user.search_user("37297553")
    print(r)
    assert r["data"]


def test_get_friends():
    r = botclient.api.user.get_friends()
    # r = userclient.api.user.get_friends()
    print(r)
    assert r["data"] is not None


def test_get_blocking_users():
    r = botclient.api.user.get_blocking_users()
    print(r)
    assert r["data"] is not None


def test_create_network_user():
    r = botclient.api.user.create_network_user()
    print(r)
    assert r["data"] is not None
