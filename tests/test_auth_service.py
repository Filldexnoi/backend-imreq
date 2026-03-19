"""
Unit tests for services/auth.py — no DB, no HTTP.
"""
import uuid
import time
import pytest
from unittest.mock import MagicMock, patch
from jose import jwt

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    authenticate_user,
    SECRET_KEY,
    ALGORITHM,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plain_text(self):
        hashed = get_password_hash("secret123")
        assert hashed != "secret123"

    def test_verify_correct_password(self):
        hashed = get_password_hash("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_reject_wrong_password(self):
        hashed = get_password_hash("correct")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes_for_same_password(self):
        """bcrypt uses random salt — hashes differ each time."""
        h1 = get_password_hash("same")
        h2 = get_password_hash("same")
        assert h1 != h2

    def test_password_over_72_bytes_truncated_consistently(self):
        """Passwords > 72 bytes are truncated — both sides must agree."""
        long_pw = "a" * 80
        hashed = get_password_hash(long_pw)
        assert verify_password(long_pw, hashed) is True

    def test_empty_password(self):
        hashed = get_password_hash("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------

class TestJWT:
    def test_create_token_returns_string(self):
        token = create_access_token({"sub": str(uuid.uuid4())})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        uid = str(uuid.uuid4())
        token = create_access_token({"sub": uid, "username": "alice"})
        data = decode_access_token(token)
        assert data is not None
        assert str(data.user_id) == uid
        assert data.username == "alice"

    def test_decode_invalid_token_returns_none(self):
        result = decode_access_token("this.is.not.a.valid.token")
        assert result is None

    def test_decode_tampered_token_returns_none(self):
        token = create_access_token({"sub": str(uuid.uuid4())})
        tampered = token[:-5] + "XXXXX"
        assert decode_access_token(tampered) is None

    def test_token_missing_sub_returns_none(self):
        """Token without 'sub' claim should return None."""
        token = create_access_token({"username": "no_sub_here"})
        result = decode_access_token(token)
        assert result is None

    def test_expired_token_returns_none(self):
        from datetime import timedelta
        token = create_access_token(
            {"sub": str(uuid.uuid4())},
            expires_delta=timedelta(seconds=-1),
        )
        assert decode_access_token(token) is None

    def test_custom_expiry_is_respected(self):
        from datetime import timedelta
        token = create_access_token(
            {"sub": "user1"},
            expires_delta=timedelta(hours=1),
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        remaining = payload["exp"] - time.time()
        assert 3500 < remaining < 3700  # ~1 hour


# ---------------------------------------------------------------------------
# authenticate_user
# ---------------------------------------------------------------------------

class TestAuthenticateUser:
    def _make_db_with_user(self, username, plain_password, is_active=True):
        import models as m
        user = MagicMock(spec=m.User)
        user.username = username
        user.hashed_password = get_password_hash(plain_password)
        user.is_active = is_active
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        return db, user

    def test_correct_credentials_return_user(self):
        db, user = self._make_db_with_user("alice", "pass123")
        result = authenticate_user(db, "alice", "pass123")
        assert result is user

    def test_wrong_password_returns_none(self):
        db, _ = self._make_db_with_user("alice", "correct")
        result = authenticate_user(db, "alice", "wrong")
        assert result is None

    def test_unknown_user_returns_none(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        result = authenticate_user(db, "ghost", "any")
        assert result is None
