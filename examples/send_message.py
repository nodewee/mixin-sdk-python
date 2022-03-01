from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth
from mixinsdk.types.message import MESSAGE_CATEGORIES, MessageRequest
from mixinsdk.types.message_data_structure import (ButtonStruct, StickerStruct,
                                                   TextStruct)
from mixinsdk.types.messenger_schema import (InvokePaymentStruct,
                                             SharingTextStruct)

from ._example_vars import (BOT_CONFIG_FILE, CNB_ASSET_ID, MY_GROUP_ID,
                            MY_USER_ID, STICKER_ID)

cfg = BotConfig.from_file(BOT_CONFIG_FILE)
bot = HttpClient_BotAuth(cfg)


def _get_conv_id_with_user(user_id):
    return bot.api.conversation.get_unique_id(cfg.client_id, user_id)


def test_send_text_message():
    # send to conversation
    r = bot.api.message.send_text(MY_GROUP_ID, "Hello, Group!")
    print(r)
    assert r["data"] is not None


def test_send_sticker_message():
    # send to user
    r = bot.api.message.send_sticker(_get_conv_id_with_user(MY_USER_ID), STICKER_ID)
    print(r)
    assert r["data"] is not None


def test_send_contact_message():
    r = bot.api.message.send_contact(MY_GROUP_ID, MY_USER_ID)
    print(r)
    assert r["data"] is not None


def test_send_messages_in_batch():
    conv_id = _get_conv_id_with_user(MY_USER_ID)

    text = "Let's go!"
    msg1 = MessageRequest(
        conv_id,
        MESSAGE_CATEGORIES.TEXT,
        TextStruct(text).to_base64(),
        recipient_id=MY_USER_ID,
    ).to_dict()

    # sticker
    msg2 = MessageRequest(
        conv_id,
        MESSAGE_CATEGORIES.STICKER,
        StickerStruct(STICKER_ID).to_base64(),
        recipient_id=MY_USER_ID,
    ).to_dict()

    bot.api.message.send_messages([msg1, msg2])


def test_send_button():
    bot.api.message.send_button(
        _get_conv_id_with_user(MY_USER_ID),
        "Open Mixin Website",
        "https://mixin.one",
        "#9999ff",
    )


def test_send_buttons_group():
    # payment button
    pay_uri = InvokePaymentStruct(
        bot.config.client_id, CNB_ASSET_ID, "0.00000001", "test"
    ).to_uri()
    pay_btn = ButtonStruct("Pay CNB", pay_uri, "#FF8000")

    # sharing button
    sharing_uri = SharingTextStruct("Hello, Mixin!").to_uri()
    sharing_btn = ButtonStruct("Share text", sharing_uri, "#99AAFF")

    # buttons group
    bot.api.message.send_button_group(
        _get_conv_id_with_user(MY_USER_ID), [pay_btn, sharing_btn]
    )
