import datetime
from pprint import pprint

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

from ._test_utils import load_app_keystore, load_parameters

TEST_PARAMS = load_parameters()
cfg = AppConfig.from_payload(load_app_keystore())
client = HttpClient_WithAppConfig(cfg)


# === user api ===


def test_read_me():
    """Read self profile of Mixin app account"""
    r = client.api.user.get_me()
    print(r)
    assert r["data"]


def test_read_user():
    user_id = "773e5e77-4107-45c2-b648-8fc722ed77f5"  # Team Mixin
    r = client.api.user.get_user(user_id)
    print(r)
    assert r["data"]


# Read multiple users
def test_read_users():
    uid_list = [
        TEST_PARAMS["user_id"],
        "773e5e77-4107-45c2-b648-8fc722ed77f5",  # Team Mixin
    ]
    r = client.api.user.get_users(uid_list)
    print(r)
    assert r["data"]


def test_search_user():
    r = client.api.user.search_user("37297553")
    print(r)
    assert r["data"]


def test_get_friends():
    r = client.api.user.get_friends()
    # r = client.api.user.get_friends()
    print(r)
    assert r["data"] is not None


def test_get_blocking_users():
    r = client.api.user.get_blocking_users()
    print(r)
    assert r["data"] is not None


def test_create_network_user():
    r = client.api.user.create_network_user()
    print(r)
    assert r["data"] is not None


# === asset api ===


def test_list_assets():
    r = client.api.asset.get_assets_list()
    print(r)
    assert r["data"] is not None


def test_get_fiat_exchange_rates():
    r = client.api.asset.get_fiat_exchange_rates()
    print(r)
    assert r["data"] is not None


# === conversation api ===


def test_read_conversation():
    user_id = TEST_PARAMS["user_id"]
    r = client.api.conversation.read(client.get_conversation_id_with_user(user_id))
    print(r)
    assert r["data"] is not None


# === message api ===


def test_attachment():
    # create attachment
    r = client.api.message.create_attachment()
    print("create attachment:", r)
    assert r["data"] is not None

    # upload attachment
    attach = r["data"]
    file = open("example-image.jpg", "rb")
    r = client.api.message.upload_attachment(attach["upload_url"], file)
    print("upload attachment:", r)

    # read attachment
    r = client.api.message.read_attachment(attach["attachment_id"])
    print("read attachment:", r)


def test_send_text_message_to_user():
    user_id = TEST_PARAMS["user_id"]
    msg_data = pack_text_data("Hello!")
    msg = pack_message(msg_data, client.get_conversation_id_with_user(user_id))
    r = client.api.send_messages(msg)
    pprint(r)
    assert r["data"] is not None


def test_send_text_message_to_group():
    group_id = TEST_PARAMS["group_id"]  # group id also is conversation id
    msg = pack_message(
        pack_text_data("Hello Group!"),
        group_id,
    )
    r = client.api.send_messages(msg)
    pprint(r)
    assert r["data"] is not None


def test_send_encrypted_message():
    user_id = TEST_PARAMS["user_id"]
    conv_id = client.get_conversation_id_with_user(user_id)
    msg_data = pack_text_data("Hi!")
    msg = pack_message(
        msg_data,
        conv_id,
        recipient_id=user_id,
        encrypt_func=client.encrypt_message_data,
    )
    msgs = [msg]
    r = client.api.message.send_encrypted_messages(msgs)
    pprint(r)
    assert r["data"] is not None


def test_send_sticker_message():
    user_id = TEST_PARAMS["user_id"]
    sticker_id = TEST_PARAMS["sticker_id"]
    msg = pack_message(
        pack_sticker_data(sticker_id), client.get_conversation_id_with_user(user_id)
    )
    r = client.api.send_messages(msg)
    print(r)
    assert r["data"] is not None


def test_send_contact():
    user_id = TEST_PARAMS["user_id"]
    msg = pack_message(
        pack_contact_data("ae45c82b-97fe-462c-97aa-b2cfc834ed4c"),
        client.get_conversation_id_with_user(user_id),
    )
    r = client.api.send_messages(msg)
    print(r)
    assert r["data"] is not None


def test_send_messages_in_batch():
    user_id = TEST_PARAMS["user_id"]
    conv_id = client.get_conversation_id_with_user(user_id)

    msg1 = pack_message(pack_text_data("Let's go!"), conv_id, recipient_id=user_id)
    msg2 = pack_message(
        pack_post_data("# title\n- [x] check item"), conv_id, recipient_id=user_id
    )
    client.api.message.send_messages([msg1, msg2])


def test_send_buttons():
    user_id = TEST_PARAMS["user_id"]
    cnb_asset_id = TEST_PARAMS["cnb_asset_id"]
    button1 = pack_button("Open Mixin Website", "https://mixin.one", "9999ff")
    pay_uri = pack_payment_uri(
        client.config.client_id, cnb_asset_id, "0.00000001", "test"
    )
    button2 = pack_button("Pay CNB", pay_uri, "FF8000")
    msg = pack_message(
        pack_button_group_data([button1, button2]),
        client.get_conversation_id_with_user(user_id),
    )
    client.api.message.send_messages(msg)


def test_send_transfer():
    user_id = TEST_PARAMS["user_id"]
    cnb_asset_id = TEST_PARAMS["cnb_asset_id"]
    r = client.api.transfer.send_to_user(user_id, cnb_asset_id, "0.00000001", "test")

    print(r)
    assert r["data"] is not None


def test_get_snapshots():
    offset = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    r = client.api.transfer.get_snapshots_list(offset, 3)
    print(r)
    assert r["data"] is not None


# === pin api ===


def test_verify_pin():
    encrypted_pin = client.get_encrypted_pin()
    r = client.api.pin.verify(encrypted_pin)
    print(r)
    assert r.get("data")


def test_get_error_logs():
    r = client.api.pin.get_error_logs()
    print(r)
    assert r.get("data")
