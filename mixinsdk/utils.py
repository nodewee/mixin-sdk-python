import datetime
import hashlib
import uuid


def base64_pad_equal_sign(s: str):
    if not len(s) % 4 == 0:
        s = s + "===="
    return s


def parse_rfc3339_to_datetime(s: str):
    """
    Params:
    - s: RFC3339Nano format, e.g. `2020-12-12T12:12:12.999999999Z`
    """
    [datestr, timestr] = s.split("T")
    [year, month, day] = datestr.split("-")
    [hour, minute, second] = timestr.split(":")
    [second, nano_sec] = second.split(".")
    microsec = int(nano_sec.rstrip("Z")[:6])

    return datetime.datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        int(microsec),
    )


def get_conversation_id_of_two_users(a_user_id, b_user_id):
    """Get conversation id of single chat between two users, such as bot and user."""
    min_id = a_user_id
    max_id = b_user_id
    if min_id > max_id:
        min_id, max_id = max_id, min_id

    md5 = hashlib.md5()
    md5.update(min_id.encode())
    md5.update(max_id.encode())
    sum = list(md5.digest())

    sum[6] = (sum[6] & 0x0F) | 0x30
    sum[8] = (sum[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(sum)))


def is_group_conversation(conversation_id, from_user_id, bot_client_id):
    """
    Check the conversation is a conversation between bot and user,
    or is a group conversation, by compare conversation_id.
    """
    u2u_conv_id = get_conversation_id_of_two_users(from_user_id, bot_client_id)
    if conversation_id == u2u_conv_id:  # single chat
        return False
    return True

    # or by request mixin api
