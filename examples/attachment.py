from examples._example_vars import APP_CONFIG_FILE
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.config import AppConfig

bot = HttpClient_WithAppConfig(AppConfig.from_file(APP_CONFIG_FILE))

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
