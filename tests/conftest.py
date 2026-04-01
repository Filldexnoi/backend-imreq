"""
Shared test fixtures for ImReq backend tests.
Uses fully-mocked DB (no real PostgreSQL needed) via FastAPI dependency overrides.
"""
import uuid
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch heavy ML imports before importing main
import unittest.mock as _mock
for _mod in ["gensim", "gensim.models", "gensim.models.doc2vec",
             "torch", "sentence_transformers",
             "sklearn", "sklearn.metrics", "sklearn.metrics.pairwise",
             "openai"]:
    if _mod not in sys.modules:
        sys.modules[_mod] = _mock.MagicMock()

def _getenv_side_effect(key, *args):
    defaults = {
        "OPENAI_API_KEY": "fake-api-key",
        "DATABASE_URL": "postgresql://fake:fake@localhost/fakedb",
    }
    return defaults.get(key, args[0] if args else None)

# Also patch SQLAlchemy create_engine so no real DB connection is attempted
with _mock.patch("os.getenv", side_effect=_getenv_side_effect), \
     _mock.patch("sqlalchemy.create_engine", return_value=_mock.MagicMock()):
    from main import app
from database import get_db
from services.auth import get_current_active_user
import models


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(**kwargs) -> models.User:
    u = MagicMock(spec=models.User)
    u.id = kwargs.get("id", uuid.uuid4())
    u.email = kwargs.get("email", "test@example.com")
    u.username = kwargs.get("username", "testuser")
    u.hashed_password = kwargs.get("hashed_password", "hashed")
    u.full_name = kwargs.get("full_name", "Test User")
    u.is_active = kwargs.get("is_active", True)
    u.is_superuser = kwargs.get("is_superuser", False)
    return u


def make_project(user_id=None, **kwargs) -> models.Project:
    p = MagicMock(spec=models.Project)
    p.id = kwargs.get("id", uuid.uuid4())
    p.user_id = user_id or uuid.uuid4()
    p.title = kwargs.get("title", "Test Project")
    p.description = kwargs.get("description", "A test project")
    p.requirement_template = kwargs.get("requirement_template", "ISO29148")
    p.reference_files = kwargs.get("reference_files", None)
    return p


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_user():
    return make_user()


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db, mock_user):
    """TestClient with mocked DB and auth."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_active_user] = lambda: mock_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client(mock_db):
    """TestClient with mocked DB but NO auth override (tests 401 paths)."""
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
