# Application case https://github.com/infowoods/oogway-mixin-bot

from mixinsdk.clients.user_config import AppConfig
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.types.message import MessageView, pack_message, pack_text_data


class MixinBotClient:
    def __init__(self):
        self.blaze: BlazeClient = None
        self.http: HttpClient_AppAuth = None


def message_handle_error_callback(error, details):
    print("error_callback --- ")
    print(f"error: {error}")
    print(f"details: {details}")


async def message_handle(message):
    global bot
    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # mixin blaze server received the message
        return

    if action == "LIST_PENDING_MESSAGES":
        print("Mixin blaze server: 👂")
        return

    if action == "ERROR":
        print(message["error"])
        return
        """example message={
            "id": "00000000-0000-0000-0000-000000000000",
            "action": "ERROR",
            "error": {
                "status": 202,
                "code": 400,
                "description": "The request body can't be parsed as valid data.",
            },
        }"""

    if action == "CREATE_MESSAGE":
        error = message.get("error")
        if error:
            print(error)
            return

        data = message["data"]
        msgview = MessageView.from_dict(data)

        if msgview.conversation_id == "":
            # is response status of send message, ignore
            return

        if msgview.type == "message":
            print(f"message from: {msgview.user_id}")

            if msgview.data_decoded == "hi":
                await bot.blaze.send_message(
                    pack_message(pack_text_data("👋 hello"), msgview.conversation_id),
                )

            await bot.blaze.echo(msgview.message_id)
            return


bot_config = AppConfig.from_file("./data/bot-config-test.json")
bot = MixinBotClient()
bot.http = HttpClient_AppAuth(bot_config)
bot.blaze = BlazeClient(
    bot_config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
)


bot.blaze.run_forever(2)
