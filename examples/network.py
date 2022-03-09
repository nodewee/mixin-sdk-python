from mixinsdk.clients.http_client import HttpClient_WithoutAuth

client = HttpClient_WithoutAuth()


def test_get_snapshots_list():
    r = client.api.network.get_snapshots_list()
    print(r)
    assert r["data"] is not None


def test_get_pending_deposits_list():
    r = client.api.network.get_pending_deposits_list()
    print(r)
    assert r["data"] is not None
