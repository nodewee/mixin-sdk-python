import datetime

from mixinsdk.clients.http_client import AppConfig, HttpClient_AppAuth

from ._example_vars import BOT_CONFIG_FILE, CNB_ASSET_ID, MY_USER_ID

client = HttpClient_AppAuth(AppConfig.from_file(BOT_CONFIG_FILE))


def test_send_transfer():
    r = client.api.transfer.send_to_user(MY_USER_ID, CNB_ASSET_ID, "0.00000001", "test")

    print(r)
    assert r["data"] is not None


def test_get_snapshots():
    offset = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    r = client.api.transfer.get_snapshots_list(offset, 3)
    print(r)
    assert r["data"] is not None
