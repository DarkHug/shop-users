import base64
import hashlib
import secrets
from typing import NamedTuple


class PKCEPair(NamedTuple):
    verifier: str
    challenge: str


def generate_pkce() -> PKCEPair:
    code_verifier = secrets.token_urlsafe(32)

    hashed = hashlib.sha256(code_verifier.encode()).digest()

    code_challenge = base64.urlsafe_b64encode(hashed).rstrip(b'=').decode()

    return PKCEPair(verifier=code_verifier, challenge=code_challenge)


def generate_state() -> str:
    return secrets.token_urlsafe(32)
