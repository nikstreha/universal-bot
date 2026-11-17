import base64
import hashlib
import hmac
import secrets
from uuid import uuid4

from universal_bot.application.port.security.secrets import ISecrets


class SecureSecrets(ISecrets):
    def identity(self) -> str:
        return str(uuid4())

    def token(self) -> str:
        return secrets.token_urlsafe(32)

    def hash(self, value: str | bytes) -> str:
        return hashlib.sha256(
            value.encode() if isinstance(value, str) else value
        ).hexdigest()

    def challenge(self, verifier: str) -> str:
        return (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )

    def matches(self, first: str, second: str) -> bool:
        return hmac.compare_digest(first, second)

    def login_code(self) -> str:
        return str(secrets.randbelow(1000000)).zfill(6)
