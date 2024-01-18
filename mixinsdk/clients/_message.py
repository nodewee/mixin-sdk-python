import base64
import json
import secrets
import logging
import uuid
from typing import List, Union

import nacl.bindings
import nacl.signing
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from mixinsdk.utils import base64_pad_equal_sign

from ..utils import base64_pad_equal_sign


def parse_message_data(
    data_b64_str: str, category: str, app_session_id: str, app_private_key: bytes
) -> Union[dict, str]:
    """
    - parse message data to str or dict. if category is ENCRYPTED_*, will decrypt message data first.

    Returns: data_parsed
    """
    if not data_b64_str:
        return ""

    if category.startswith("ENCRYPTED_"):
        d = decrypt_message_data(data_b64_str, app_session_id, app_private_key)
    else:
        d = base64.b64decode(data_b64_str).decode()

    if category.endswith(("_TEXT", "_POST")):
        return d
    try:
        return json.loads(d)
    except json.JSONDecodeError:
        logging.error(f"Failed to json decode data_b64_str: {d}")


def decrypt_message_data(data_b64_str: str, app_session_id: str, private: bytes):
    data_bytes = base64.b64decode(base64_pad_equal_sign(data_b64_str))  # not url safe
    size = 16 + 48  # length of session id bytes + length of encrypted shared key bytes
    total = len(data_bytes)
    # bytes([1]) + session_len + pub_key + session_id + shared_key + nonce + ...data
    if total < 1 + 2 + 32 + 16 + 48 + 12:
        raise ValueError("Invalid message data")
    session_length = int.from_bytes(data_bytes[1:3], byteorder="little")
    prefixSize = 35 + session_length * size
    key = []
    for i in range(35, prefixSize, size):
        uid = str(uuid.UUID(bytes=data_bytes[i : i + 16]))
        if uid == app_session_id:
            dst = []
            priv = []
            pub = []
            pub = data_bytes[3:35]

            priv = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(private)
            dst = nacl.bindings.crypto_scalarmult(priv, pub)

            block_size = 16
            iv = data_bytes[i + 16 : i + 16 + block_size]
            key = data_bytes[i + 16 + block_size : i + size]
            decryptor = Cipher(algorithms.AES(dst), modes.CBC(iv)).decryptor()
            key = decryptor.update(key)  # do not: + decryptor.finalize()
            key = key[:16]
            break

    if len(key) != 16:
        raise ValueError("Invalid key")

    encrypted_data = data_bytes[prefixSize + 12 : -16]  # remove nonce and tag

    nonce = data_bytes[prefixSize : prefixSize + 12]
    decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).decryptor()
    plain_text = decryptor.update(encrypted_data)
    return plain_text.decode()


def encrypt_message_data(
    data_bytes: bytes, recipient_sessions: List[dict], app_private_key: bytes
):
    """
    session struct: {user_id:uuid str, session_id:uuid str, public_key:str}
    """

    shared_key = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)

    encryptor = Cipher(algorithms.AES(shared_key), modes.GCM(nonce)).encryptor()
    shared_ciphertext = encryptor.update(data_bytes)
    shared_ciphertext += encryptor.finalize() + encryptor.tag  # tag = +16 bytes

    # ed25519 private key -> cureve25519 public key
    _pk = nacl.bindings.crypto_sign_ed25519_sk_to_pk(app_private_key)
    curve25519_pubkey = nacl.bindings.crypto_sign_ed25519_pk_to_curve25519(_pk)

    # ed25519 private key -> curve25519 private key
    curve25519_privkey = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(
        app_private_key
    )

    padding = 16 - len(shared_key) % 16  # = 16
    pad_text = bytes([padding] * padding)
    shared_key += pad_text  # length = 32

    sessions_bytes = b""
    for s in recipient_sessions:
        client_pub = base64.urlsafe_b64decode(base64_pad_equal_sign(s["public_key"]))
        p2p_key = nacl.bindings.crypto_scalarmult(curve25519_privkey, client_pub)

        iv = secrets.token_bytes(16)
        encryptor = Cipher(algorithms.AES(p2p_key), modes.CBC(iv)).encryptor()
        encrypted_shared_key = iv + encryptor.update(shared_key)
        encrypted_shared_key += encryptor.finalize()  # length = 48

        id_ = uuid.UUID(s["session_id"]).bytes
        sessions_bytes += id_ + encrypted_shared_key
    session_len = len(recipient_sessions).to_bytes(2, byteorder="little")

    result = (
        bytes([1])
        + session_len
        + curve25519_pubkey
        + sessions_bytes
        + nonce
        + shared_ciphertext
    )
    encoded = base64.urlsafe_b64encode(result).decode("utf-8")  # must be url safe
    encoded = encoded.rstrip("=")  # remove padding

    return encoded
