from mixinsdk.clients.bot_config import BotConfig
from mixinsdk.clients.http_client import (HttpClient_BotAuth,
                                          HttpClient_UserAuth)

from ._example_vars import BOT_CONFIG_FILE, MY_USER_ID, USER_AUTH_TOKEN

cfg = BotConfig.from_file(BOT_CONFIG_FILE)
botclient = HttpClient_BotAuth(cfg)
userclient = HttpClient_UserAuth(USER_AUTH_TOKEN)


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
    uids = [MY_USER_ID, botclient.config.client_id]
    r = botclient.api.user.get_users(uids)
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
