import sys

from mixinsdk.clients.client_http_nosign import HttpClient_WithAccessToken

from ._test_utils import load_parameters

TEST_PARAMS = load_parameters()
USER_AUTH_TOKEN = TEST_PARAMS.get("user_auth_token")
if not USER_AUTH_TOKEN:
    print("✗ No user auth token found in test parameters file")
    sys.exit(0)
client = HttpClient_WithAccessToken(USER_AUTH_TOKEN)


# Read self profile with User's oauth access token
def test_read_me_of_user():
    r = client.api.user.get_me()
    print(r)
    assert r["data"]
