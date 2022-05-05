from mixinsdk.clients.http_client import BotConfig, HttpClient_BotAuth
from mixinsdk.types.message import (
    MessageDataObject,
    pack_button,
    pack_button_group_data,
    pack_contact_data,
    pack_message,
    pack_text_data,
    pack_post_data,
    pack_sticker_data,
)
from mixinsdk.types.messenger_schema import pack_payment_uri

from ._example_vars import (
    BOT_CONFIG_FILE,
    CNB_ASSET_ID,
    MY_GROUP_ID,
    MY_USER_ID,
    STICKER_ID,
)

bot = HttpClient_BotAuth(BotConfig.from_file(BOT_CONFIG_FILE))


def test_send_text_message():
    # send message to group
    msg = pack_message(pack_text_data("Hello, Group!"), MY_GROUP_ID)
    r = bot.api.send_messages(msg)
    print(r)
    assert r["data"] is not None


def test_send_sticker_message():
    # send to user
    msg = pack_message(
        pack_sticker_data(STICKER_ID), bot.get_conversation_id_with_user(MY_USER_ID)
    )
    r = bot.api.send_messages(msg)
    print(r)
    assert r["data"] is not None


def test_send_contact():
    msg = pack_message(pack_contact_data(MY_USER_ID), MY_GROUP_ID)
    r = bot.api.send_messages(msg)
    print(r)
    assert r["data"] is not None


def test_send_messages_in_batch():
    conv_id = bot.get_conversation_id_with_user(MY_USER_ID)

    msg1 = pack_message(pack_text_data("Let's go!"), conv_id, recipient_id=MY_USER_ID)
    msg2 = pack_message(
        pack_post_data("# title\n- [x] check item"), conv_id, recipient_id=MY_USER_ID
    )
    bot.api.message.send_messages([msg1, msg2])


def test_send_buttons():
    button1 = pack_button("Open Mixin Website", "https://mixin.one", "9999ff")
    pay_uri = pack_payment_uri(bot.config.client_id, CNB_ASSET_ID, "0.00000001", "test")
    button2 = pack_button("Pay CNB", pay_uri, "FF8000")
    msg = pack_message(
        pack_button_group_data([button1, button2]),
        bot.get_conversation_id_with_user(MY_USER_ID),
    )
    bot.api.message.send_messages(msg)


def test_send(msg_data_obj: MessageDataObject):
    msg = pack_message(
        msg_data_obj,
        bot.get_conversation_id_with_user(MY_USER_ID),
    )
    bot.api.message.send_messages(msg)
