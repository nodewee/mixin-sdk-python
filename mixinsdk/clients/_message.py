import base64
import uuid
import os
from mixinsdk.types.user import UserSession
from mixinsdk.utils import base64_pad_equal_sign

import nacl.bindings
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from typing import List, Union
from ..types.message import MESSAGE_CATEGORIES
import json
from cryptography.hazmat.primitives.asymmetric import ed25519


def parse_message_data(
    data: str, category: str, app_session_id: str, app_private_key: bytes
) -> Union[dict, str]:
    """
    - parse message data (Base64 encoded string) to str or dict
    - decrypt message data if category is ENCRYPTED_

    Returns: data_parsed
    """
    if not data:
        return ""

    if category.startswith("ENCRYPTED_"):
        d = decrypt_message_data(data, app_session_id, app_private_key)
        print("\ndecrypted:", d)
    else:
        d = base64.b64decode(data).decode()

    if category.endswith(("_TEXT", "_POST")):
        return d
    try:
        return json.loads(d)
    except json.JSONDecodeError:
        print(f"Failed to json decode data: {d}")


def decrypt_message_data(data_b64_str: str, app_session_id: str, private: bytes):
    data_bytes = base64.b64decode(base64_pad_equal_sign(data_b64_str))
    size = 16 + 48  # session id bytes + encrypted key bytes size
    total = len(data_bytes)
    if total < 1 + 2 + 32 + size + 12:
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
            cipher = Cipher(algorithms.AES(dst), modes.CBC(iv))
            encryptor = cipher.decryptor()
            key = encryptor.update(key)  # do not: + encryptor.finalize()
            key = key[:16]
            break

    if len(key) != 16:
        raise ValueError("Invalid key")

    encrypted_data = data_bytes[prefixSize + 12 : -16]  # ? -16 是根据结果错误输出来的，go 的代码没有-16

    nonce = data_bytes[prefixSize : prefixSize + 12]
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.decryptor()
    plain_text = encryptor.update(encrypted_data)
    return plain_text.decode()


def encrypt_message_data(
    data_b64_str: str, user_sessions: List[UserSession], app_private_key: bytes
):
    data_bytes = base64.b64decode(data_b64_str)

    """
    key := make([]byte, 16)
    _, err = rand.Read(key)
    if err != nil {
    return "", err
    }
    nonce := make([]byte, 12)
    _, err = rand.Read(nonce)
    if err != nil {
    return "", err
    }
    block, err := aes.NewCipher(key)
    if err != nil {
    return "", err
    }
    aesgcm, err := cipher.NewGCM(block)
    if err != nil {
    return "", err
    }
    ciphertext := aesgcm.Seal(nil, nonce, data_bytes, nil)
    """
    block_size = 16
    key = os.urandom(block_size)
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data_bytes)  # do not: + encryptor.finalize()

    session_length = len(user_sessions)
    session_length = session_length.to_bytes(2, byteorder="little")

    # private := ed25519.PrivateKey(privateBytes)
    # pub, _ := PublicKeyToCurve25519(ed25519.PublicKey(private[32:]))
    private = ed25519.Ed25519PrivateKey().from_private_bytes(app_private_key)
    public = private.public_key()
    priv_curve25519 = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(private)
    pub_curve25519 = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(public)

    session_bytes = bytearray()
    # for _, s := range sessions {
    for s in user_sessions:
        # 	clientPublic, err := base64.RawURLEncoding.DecodeString(s.PublicKey)
        client_public = base64.b64decode(s.public_key)
        # 	var dst, priv, clientPub [32]byte
        # 	copy(clientPub[:], clientPublic[:])
        client_pub = client_public[:32]

        # 	curve25519.ScalarMult(&dst, &priv, &clientPub)
        dst = nacl.bindings.crypto_scalarmult(priv_curve25519, client_pub)

        # 	padding := aes.BlockSize - len(key)%aes.BlockSize
        padding = block_size - len(key) % block_size
        padtext = bytes(padding) * padding
        # 	copy(shared[:], key[:])
        shared = key[:]
        # shared = append(shared, padtext...)
        shared += padtext
        # 	ciphertext := make([]byte, aes.BlockSize+len(shared))
        # 	iv := ciphertext[:aes.BlockSize]
        iv = os.urandom(block_size + len(shared))
        # 	mode := cipher.NewCBCEncrypter(block, iv)
        # 	mode.CryptBlocks(ciphertext[aes.BlockSize:], shared)
        # 	block, err := aes.NewCipher(dst[:])
        cipher = Cipher(algorithms.AES(dst), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(shared)
        # 	id, err := UuidFromString(s.SessionID)
        id = uuid.UUID(s.session_id)
        # 	sessionsBytes = append(sessionsBytes, id.Bytes()...)
        # 	sessionsBytes = append(sessionsBytes, ciphertext...)
        session_bytes.append(id.bytes)
        session_bytes.append(ciphertext)

    # result := []byte{1}
    result = bytearray()
    # result = append(result, sessionLen[:]...)
    result.append(session_length)
    # result = append(result, pub[:]...)
    result.append(pub_curve25519)
    # result = append(result, sessionsBytes...)
    result.extend(session_bytes)
    # result = append(result, nonce[:]...)
    result.extend(nonce)
    # result = append(result, ciphertext...)
    result.extend(ciphertext)
    # return base64.RawURLEncoding.EncodeToString(result), nil
    return base64.b64encode(result)
