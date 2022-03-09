import asyncio

from mixinsdk.clients.blaze_client import BlazeClient, BotConfig
from mixinsdk.types.message import MESSAGE_CATEGORIES, MessageRequest, MessageView
from mixinsdk.types.message_data_structure import ContactStruct, TextStruct

from ._example_vars import MY_USER_ID


async def handle_text_message_from_me(client: BlazeClient, msgview: MessageView):
    cmd = msgview.data_parsed.text.lower()
    if cmd == "hi":
        data = TextStruct("Hi, I'm robot.").to_base64()
        msg = MessageRequest(
            msgview.conversation_id,
            MESSAGE_CATEGORIES.TEXT,
            data,
            recipient_id=msgview.user_id,
        ).to_dict()
        await client.send_message(msg)
    elif cmd == "contact":
        data = ContactStruct(MY_USER_ID).to_base64()
        msg = MessageRequest(
            msgview.conversation_id,
            MESSAGE_CATEGORIES.CONTACT,
            data,
            recipient_id=msgview.user_id,
        ).to_dict()
        await client.send_message(msg)


async def on_message(client: BlazeClient, message):
    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # blaze server received the message
        return

    if action == "LIST_PENDING_MESSAGES":
        print("Blaze Server:👂")
        return

    if action == "ERROR":
        print(message["error"])
        return
        """message={
            "id": "00000000-0000-0000-0000-000000000000",
            "action": "ERROR",
            "error": {
                "status": 202,
                "code": 400,
                "description": "The request body can't be parsed as valid data.",
            },
        }"""

    if action == "CREATE_MESSAGE":
        data = message["data"]
        msgview = MessageView.from_dict(data)
        if msgview.type == "message":
            if msgview.category == MESSAGE_CATEGORIES.TEXT:
                if msgview.user_id == MY_USER_ID:
                    await handle_text_message_from_me(client, msgview)
            await client.echo(msgview.message_id)
            return

    print("Unknown message:", message)


def start_client():
    config = BotConfig.from_file("./data/bot-config-test.json")
    client = BlazeClient(config, on_message=on_message)

    async def start():
        await client.run()

    asyncio.run(start())
