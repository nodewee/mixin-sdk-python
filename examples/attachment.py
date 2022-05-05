from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth
from ._example_vars import BOT_CONFIG_FILE

bot = HttpClient_BotAuth(BotConfig.from_file(BOT_CONFIG_FILE))

# create attachment
r = bot.api.message.create_attachment()
print(r)

# upload attachment
attach = r["data"]
file = open("example-image.jpg", "rb")
r = bot.api.message.upload_attachment(attach["upload_url"], file)
print(r)

# read attachment
r = bot.api.message.read_attachment(attach["attachment_id"])
print(r)
