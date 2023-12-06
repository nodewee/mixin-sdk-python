import base64
import json
import secrets
import uuid
from typing import List, Union

import nacl.bindings
import nacl.signing
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from nacl.encoding import RawEncoder
from nacl.signing import SigningKey

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
        # print("\ndecrypted:", d)
    else:
        d = base64.b64decode(data_b64_str).decode()

    if category.endswith(("_TEXT", "_POST")):
        return d
    try:
        return json.loads(d)
    except json.JSONDecodeError:
        print(f"Failed to json decode data_b64_str: {d}")


def decrypt_message_data(data_b64_str: str, app_session_id: str, private: bytes):
    data_bytes = base64.b64decode(base64_pad_equal_sign(data_b64_str))
    size = 16 + 48  # session id bytes + shared key bytes size
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

    encrypted_data = data_bytes[prefixSize + 12 : -16]  # ?len(finalize() + .tag) = 16

    nonce = data_bytes[prefixSize : prefixSize + 12]
    decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).decryptor()
    plain_text = decryptor.update(encrypted_data)
    return plain_text.decode()


def encrypt_message_data(
    data_bytes: bytes, user_sessions: List[dict], app_private_key: bytes
):
    """
    session struct: {user_id:uuid str, session_id:uuid str, public_key:str}
    """

    key = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)

    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    main_ciphertext = encryptor.update(data_bytes)
    main_ciphertext += encryptor.finalize() + encryptor.tag

    # ed25519 private key -> cureve25519 public key
    _pk = nacl.bindings.crypto_sign_ed25519_sk_to_pk(app_private_key)
    curve25519_pubkey = nacl.bindings.crypto_sign_ed25519_pk_to_curve25519(_pk)

    # ed25519 private key -> curve25519 private key
    curve25519_privkey = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(
        app_private_key
    )

    session_len = len(user_sessions).to_bytes(2, byteorder="little")
    sessions_bytes = b""

    padding = 16 - len(key) % 16
    pad_text = bytes([padding] * padding)
    shared = key + pad_text

    for s in user_sessions:
        client_pub = base64.urlsafe_b64decode(base64_pad_equal_sign(s["public_key"]))
        dst = nacl.bindings.crypto_scalarmult(curve25519_privkey, client_pub)

        iv = secrets.token_bytes(16)
        encryptor = Cipher(algorithms.AES(dst), modes.CBC(iv)).encryptor()
        ciphertext = iv + encryptor.update(shared)  # do not: + encryptor.finalize()

        id = uuid.UUID(s["session_id"]).bytes
        sessions_bytes += id + ciphertext

    result = (
        bytes([1])
        + session_len
        + curve25519_pubkey
        + sessions_bytes
        + nonce
        + main_ciphertext
    )
    encoded = base64.urlsafe_b64encode(result).decode("utf-8")
    encoded = encoded.rstrip("=")  # remove padding

    return encoded
