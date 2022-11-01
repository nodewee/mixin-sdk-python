import sys
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.config import AppConfig

from mixinsdk.types.message import (
    MessageDataObject,
    pack_button,
    pack_button_group_data,
    pack_contact_data,
    pack_message,
    pack_post_data,
    pack_sticker_data,
    pack_text_data,
)
from mixinsdk.types.messenger_schema import pack_payment_uri

from ._example_vars import (
    APP_CONFIG_FILE,
    CNB_ASSET_ID,
    MY_GROUP_ID,
    MY_USER_ID,
    STICKER_ID,
)

if not MY_USER_ID:
    print("✘ Please fill MY_USER_ID in _example_vars.py")
    sys.exit(0)

if not MY_GROUP_ID:
    print("✘ Please fill MY_GROUP_ID in _example_vars.py")
    sys.exit(0)

bot = HttpClient_WithAppConfig(AppConfig.from_file(APP_CONFIG_FILE))


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


# def test_send(msg_data_obj: MessageDataObject):
#     msg = pack_message(
#         msg_data_obj,
#         bot.get_conversation_id_with_user(MY_USER_ID),
#     )
#     bot.api.message.send_messages(msg)
