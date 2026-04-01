"""
Extended tests for services/auth.py
Covers: get_current_user (invalid token, user not found), get_current_active_user (inactive)
"""
import uuid
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from services.auth import (
    get_current_user,
    get_current_active_user,
    decode_access_token,
    create_access_token,
)


def _make_user(**kw):
    u = MagicMock(spec=models.User)
    u.id = kw.get("id", str(uuid.uuid4()))
    u.username = kw.get("username", "testuser")
    u.is_active = kw.get("is_active", True)
    return u


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        db = MagicMock()
        with patch("services.auth.decode_access_token", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await get_current_user(token="bad.token", db=db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_no_user_id_raises_401(self):
        db = MagicMock()
        token_data = MagicMock()
        token_data.user_id = None
        with patch("services.auth.decode_access_token", return_value=token_data):
            with pytest.raises(HTTPException) as exc:
                await get_current_user(token="token", db=db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_user_not_in_db_raises_401(self):
        db = MagicMock()
        token_data = MagicMock()
        token_data.user_id = str(uuid.uuid4())
        db.query.return_value.filter.return_value.first.return_value = None
        with patch("services.auth.decode_access_token", return_value=token_data):
            with pytest.raises(HTTPException) as exc:
                await get_current_user(token="token", db=db)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        db = MagicMock()
        user = _make_user()
        token_data = MagicMock()
        token_data.user_id = str(user.id)
        db.query.return_value.filter.return_value.first.return_value = user
        with patch("services.auth.decode_access_token", return_value=token_data):
            result = await get_current_user(token="valid.token", db=db)
        assert result == user


class TestGetCurrentActiveUser:
    @pytest.mark.asyncio
    async def test_inactive_user_raises_400(self):
        inactive = _make_user(is_active=False)
        with pytest.raises(HTTPException) as exc:
            await get_current_active_user(current_user=inactive)
        assert exc.value.status_code == 400
        assert "Inactive" in exc.value.detail

    @pytest.mark.asyncio
    async def test_active_user_passes(self):
        active = _make_user(is_active=True)
        result = await get_current_active_user(current_user=active)
        assert result == active
