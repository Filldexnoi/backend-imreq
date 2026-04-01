"""
Tests for routers/auth.py — register, login, me, update_me, logout.
"""
import uuid
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models


def _make_user(**kwargs):
    u = MagicMock(spec=models.User)
    u.id = kwargs.get("id", uuid.uuid4())
    u.email = kwargs.get("email", "user@example.com")
    u.username = kwargs.get("username", "testuser")
    u.full_name = kwargs.get("full_name", "Test User")
    u.hashed_password = kwargs.get("hashed_password", "hashed_pw")
    u.is_active = kwargs.get("is_active", True)
    u.is_superuser = kwargs.get("is_superuser", False)
    u.last_login = kwargs.get("last_login", None)
    u.created_at = kwargs.get("created_at", datetime.utcnow())
    return u


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success(self, client, mock_db):
        # email not found, username not found → success
        new_user = _make_user()
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, None]
        mock_db.refresh.side_effect = lambda obj: None

        with patch("routers.auth.get_password_hash", return_value="hashed_pw"):
            with patch("routers.auth.models.User", return_value=new_user):
                resp = client.post("/api/auth/register", json={
                    "email": "new@example.com",
                    "username": "newuser",
                    "password": "secret123",
                    "full_name": "New User"
                })
        assert resp.status_code == 201
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_register_duplicate_email(self, client, mock_db):
        existing = _make_user()
        # First query (email) returns existing user → 400
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        resp = client.post("/api/auth/register", json={
            "email": "existing@example.com",
            "username": "newuser",
            "password": "secret123",
            "full_name": "New User"
        })
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]

    def test_register_duplicate_username(self, client, mock_db):
        existing = _make_user()
        # email not found, username found → 400
        mock_db.query.return_value.filter.return_value.first.side_effect = [None, existing]

        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "username": "existing",
            "password": "secret123",
            "full_name": "New User"
        })
        assert resp.status_code == 400
        assert "Username already taken" in resp.json()["detail"]

    def test_register_missing_fields(self, client):
        resp = client.post("/api/auth/register", json={"email": "x@x.com"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self, client, mock_db):
        user = _make_user()
        with patch("routers.auth.authenticate_user", return_value=user), \
             patch("routers.auth.create_access_token", return_value="fake.jwt.token"):
            resp = client.post("/api/auth/login", json={
                "identifier": "testuser",
                "password": "secret123"
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "fake.jwt.token"
        assert data["token_type"] == "bearer"
        assert mock_db.commit.called

    def test_login_with_email(self, client, mock_db):
        user = _make_user()
        with patch("routers.auth.authenticate_user", return_value=user), \
             patch("routers.auth.create_access_token", return_value="fake.jwt.token"):
            resp = client.post("/api/auth/login", json={
                "identifier": "test@example.com",
                "password": "secret123"
            })
        assert resp.status_code == 200

    def test_login_wrong_credentials(self, client, mock_db):
        with patch("routers.auth.authenticate_user", return_value=None):
            resp = client.post("/api/auth/login", json={
                "identifier": "wrong",
                "password": "wrong"
            })
        assert resp.status_code == 401
        assert "Incorrect username or password" in resp.json()["detail"]

    def test_login_inactive_user(self, client, mock_db):
        user = _make_user(is_active=False)
        with patch("routers.auth.authenticate_user", return_value=user):
            resp = client.post("/api/auth/login", json={
                "identifier": "testuser",
                "password": "secret123"
            })
        assert resp.status_code == 403
        assert "inactive" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------------

class TestGetMe:
    def test_get_me_success(self, client, mock_user):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.json()["username"] == mock_user.username

    def test_get_me_unauthorized(self, anon_client):
        resp = anon_client.get("/api/auth/me")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /api/auth/me
# ---------------------------------------------------------------------------

class TestUpdateMe:
    def test_update_full_name(self, client, mock_db, mock_user):
        mock_user.full_name = "Old Name"
        mock_db.refresh.side_effect = lambda obj: None

        resp = client.put("/api/auth/me", json={"full_name": "New Name"})
        assert resp.status_code == 200
        assert mock_db.commit.called

    def test_update_email_success(self, client, mock_db, mock_user):
        mock_user.email = "old@example.com"
        mock_db.query.return_value.filter.return_value.first.return_value = None  # no conflict
        mock_db.refresh.side_effect = lambda obj: None

        resp = client.put("/api/auth/me", json={"email": "new@example.com"})
        assert resp.status_code == 200

    def test_update_email_conflict(self, client, mock_db, mock_user):
        mock_user.email = "old@example.com"
        other_user = _make_user(email="taken@example.com")
        mock_db.query.return_value.filter.return_value.first.return_value = other_user

        resp = client.put("/api/auth/me", json={"email": "taken@example.com"})
        assert resp.status_code == 400
        assert "Email already in use" in resp.json()["detail"]

    def test_update_username_success(self, client, mock_db, mock_user):
        mock_user.username = "old_name"
        # email query not triggered (no email change), username query returns None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.refresh.side_effect = lambda obj: None

        resp = client.put("/api/auth/me", json={"username": "new_name"})
        assert resp.status_code == 200

    def test_update_username_conflict(self, client, mock_db, mock_user):
        mock_user.username = "old_name"
        other = _make_user(username="taken")
        mock_db.query.return_value.filter.return_value.first.return_value = other

        resp = client.put("/api/auth/me", json={"username": "taken"})
        assert resp.status_code == 400
        assert "Username already taken" in resp.json()["detail"]

    def test_update_password(self, client, mock_db, mock_user):
        mock_db.refresh.side_effect = lambda obj: None
        with patch("routers.auth.get_password_hash", return_value="new_hashed"):
            resp = client.put("/api/auth/me", json={"password": "newpassword"})
        assert resp.status_code == 200
        assert mock_user.hashed_password == "new_hashed"


# ---------------------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_success(self, client):
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert "logged out" in resp.json()["message"]

    def test_logout_unauthorized(self, anon_client):
        resp = anon_client.post("/api/auth/logout")
        assert resp.status_code == 401
