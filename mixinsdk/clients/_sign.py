import datetime
import hashlib
import os
import time
import uuid
from base64 import urlsafe_b64decode, urlsafe_b64encode

import jwt
import nacl.bindings
import nacl.signing
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import padding as _padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def sign_authentication_token(
    user_id, session_id, private_key, key_algorithm, method, uri, bodystring: str = None
):
    """
    JWT Structure: https://developers.mixin.one/docs/api/guide
    """

    if key_algorithm.lower() in ["rs512", "rsa"]:
        alg = "RS512"
        key = private_key
    elif key_algorithm.lower() in ["eddsa", "ed25519"]:
        alg = "EdDSA"
        key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key[:32])
    else:
        raise ValueError(f"Unsupported key's algorithm: {key_algorithm}")

    jwt_headers = {
        "alg": alg,
        "typ": "JWT",
    }

    bodystring = bodystring if bodystring else ""
    hashresult = hashlib.sha256((method + uri + bodystring).encode("utf-8")).hexdigest()
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=200)
    payload = {
        "uid": user_id,
        "sid": session_id,
        "iat": datetime.datetime.utcnow(),
        "exp": exp,
        "jti": str(uuid.uuid4()),
        "sig": hashresult,
        "scp": "FULL",
    }

    return jwt.encode(payload, key, algorithm=alg, headers=jwt_headers)


def encrypt_pin(
    pin, pin_token, private_key, key_algorithm, session_id, iter_string: str = None
):
    """Support RS512 and Ed25519 algorithm"""
    pin_token_bytes = urlsafe_b64decode(pin_token)

    # Get pin key
    if key_algorithm == "RS512":
        # load RSA key from PEM format
        private_key = serialization.load_pem_private_key(
            private_key.encode(), password=None
        )
        # decrypt
        pin_key = private_key.decrypt(
            pin_token_bytes,
            _padding.OAEP(
                mgf=_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=session_id.encode("utf-8"),
            ),
        )
    elif key_algorithm == "Ed25519":
        # ed25519 to curve25519
        curve25519_key = nacl.bindings.crypto_sign_ed25519_sk_to_curve25519(private_key)
        # scalar multiplication: curve25519_key * public
        pin_key = nacl.bindings.crypto_scalarmult(curve25519_key, pin_token_bytes)
    else:
        raise ValueError(f"Invalid key algorithm: {key_algorithm}")

    # Prepare content to be encrypted
    pin_bytes = pin.encode("utf-8")
    be_encrypt = pin_bytes
    # append timestamp bytes
    timebytes = int(time.time()).to_bytes(8, "little")  # unix timestamp
    be_encrypt += timebytes
    # append iterator bytes
    if iter_string:
        iterator_bytes = iter_string.encode("utf-8")
    else:
        iterator_bytes = int(time.time() * 1e9).to_bytes(8, "little")  # unix nano
    be_encrypt += iterator_bytes
    # append padding bytes
    block_size = 16
    padding_num = block_size - len(be_encrypt) % block_size
    padding_bytes = int.to_bytes(padding_num, 1, "little") * padding_num
    be_encrypt += padding_bytes

    # Encrypt (use AES-256-CBC)
    iv = os.urandom(block_size)
    cipher = Cipher(algorithms.AES(pin_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(be_encrypt)  # do not: + encryptor.finalize()
    #
    encrypted_pin = iv + ciphertext
    encrypted_pin = urlsafe_b64encode(encrypted_pin).decode()
    return encrypted_pin


def generate_ed25519_keypair():
    "return (public_key, private_key)"
    signing_key = nacl.signing.SigningKey.generate()
    pk = signing_key.verify_key._key
    sk = signing_key._signing_key
    return (pk, sk)
