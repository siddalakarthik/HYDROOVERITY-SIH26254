"""Opaque sessions, bounded privacy-preserving throttles and private local mail."""

import hashlib
import hmac
import json
import secrets
import threading
import time
from collections import OrderedDict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError

from .errors import require

PASSWORDS = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1, type=Type.ID)
DUMMY = PASSWORDS.hash(secrets.token_urlsafe(32))
COOKIE = "__Host-hydro_session"


def now() -> datetime:
    return datetime.now(UTC)


def secret() -> str:
    return secrets.token_urlsafe(32)


def verifier(value: str) -> bytes:
    return hashlib.sha256(value.encode()).digest()


def password_matches(encoded: str, password: str) -> bool:
    try:
        return PASSWORDS.verify(encoded, password)
    except VerificationError:
        return False


class Limits:
    """Single-process pilot only. Saturation fails closed, never evicts active limits."""

    def __init__(self, key: str):
        self.key = key.encode()
        self.buckets: OrderedDict[str, tuple[float, int]] = OrderedDict()
        self.lock = threading.Lock()

    def hit(self, action: str, identity: str, maximum: int, window: int) -> None:
        instant = time.time()
        daily = hmac.digest(self.key, str(int(instant // 86400)).encode(), "sha256")
        bucket = hmac.new(daily, (action + ":" + identity).encode(), "sha256").hexdigest()
        with self.lock:
            expired = [k for k, (until, _) in self.buckets.items() if until <= instant]
            for k in expired:
                del self.buckets[k]
            require(
                bucket in self.buckets or len(self.buckets) < 10000,
                503,
                "RATE_CAPACITY",
                "Rate limiter capacity reached",
            )
            until, count = self.buckets.get(bucket, (instant + min(window, 86400), 0))
            self.buckets[bucket] = (until, count + 1)
            require(count < maximum, 429, "RATE_LIMITED", "Please retry after the limit window")


class PrivateMail:
    """Post-commit development adapter; private filesystem, never a public route.

    Operator must use a user-private directory outside the checkout. On POSIX,
    directory/file modes are 0700/0600. Windows inherits the operator directory ACL.
    No external message was sent. Expired files are deleted before each delivery.
    """

    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.lock = threading.Lock()

    def deliver(self, purpose: str, recipient: str, token: str) -> None:
        with self.lock:
            try:
                self._deliver(purpose, recipient, token)
            except OSError:
                # A failed local delivery never changes the generic committed reply.
                return

    def _deliver(self, purpose: str, recipient: str, token: str) -> None:
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        files = list(self.directory.glob("*.json"))
        for p in files:
            if time.time() - p.stat().st_mtime > 1800:
                p.unlink()
        if len(list(self.directory.glob("*.json"))) >= 100:
            return
        p = self.directory / (str(uuid4()) + ".json")
        try:
            with p.open("x", encoding="utf-8") as f:
                p.chmod(0o600)
                json.dump(
                    {
                        "development_only": True,
                        "purpose": purpose,
                        "recipient": recipient,
                        "token": token,
                        "expires_at": (now() + timedelta(minutes=30)).isoformat(),
                    },
                    f,
                )
        except OSError:
            # Token never enters a log or the tenant outbox; retry after cooldown.
            return
