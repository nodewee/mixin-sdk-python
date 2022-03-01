from mixinsdk.clients.http_client import HttpClient_WithouAuth

client = HttpClient_WithouAuth()


def test_get_sanpshots_lsit():
    r = client.api.network.get_snapshots_list()
    print(r)
    assert r["data"] is not None


def test_get_pending_deposits_list():
    r = client.api.network.get_pending_deposits_list()
    print(r)
    assert r["data"] is not None
