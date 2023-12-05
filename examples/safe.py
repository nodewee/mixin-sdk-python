import json

from examples._example_vars import APP_CONFIG_FILE, CNB_ASSET_ID
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.config import AppConfig
from mixinsdk.types.messenger_schema import pack_payment_uri

bot = HttpClient_WithAppConfig(AppConfig.from_file(APP_CONFIG_FILE))

# check if bot update to safe version
resp = bot.api.user.get_me()
assert resp["data"]["has_safe"] == True

# pack pay uri of safe version
amount = "1.23456"
memo = "test_again"
uri = pack_payment_uri(bot.config.client_id, CNB_ASSET_ID, amount, memo, version="safe")
print(uri)

# open uri in browser and pay for it with user which updated to safe version

# get snapshots list of safe version
snapshots = bot.api.transfer.get_snapshots_list(limit=10, version="safe")
print(json.dumps(snapshots, indent=4))
