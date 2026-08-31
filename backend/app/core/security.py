import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings

_ph = PasswordHasher()


def encrypt_aes_gcm(plaintext: str, key: bytes) -> bytes:
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt_aes_gcm(ciphertext: bytes, key: bytes) -> str:
    nonce = ciphertext[:12]
    encrypted = ciphertext[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, encrypted, None)
    return plaintext.decode("utf-8")


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hash: str) -> bool:
    try:
        return _ph.verify(hash, password)
    except Exception:
        return False


def create_access_token(user_id: int, data: dict, expires_delta: timedelta) -> str:
    payload = {
        "sub": str(user_id),
        **data,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt.secret_key, algorithm="HS256")


def create_refresh_token(user_id: int, data: dict, expires_delta: timedelta) -> str:
    payload = {
        "sub": str(user_id),
        **data,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def generate_sse_ticket() -> str:
    return secrets.token_urlsafe(32)