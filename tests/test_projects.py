"""
Integration-style tests for project CRUD endpoints in main.py.
DB and auth are fully mocked via FastAPI dependency overrides.
"""
import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models


def _make_project(user_id, **kw):
    p = MagicMock(spec=models.Project)
    p.id = kw.get("id", uuid.uuid4())
    p.user_id = user_id
    p.title = kw.get("title", "Test Project")
    p.description = kw.get("description", "Desc")
    p.requirement_template = kw.get("requirement_template", "ISO29148")
    p.reference_files = kw.get("reference_files", None)
    p.created_at = kw.get("created_at", datetime.now(timezone.utc))
    p.updated_at = kw.get("updated_at", None)
    return p


class TestGetProjects:
    def test_returns_empty_list(self, client, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.offset.return_value \
            .limit.return_value.all.return_value = []
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_project_list(self, client, mock_db, mock_user):
        p = _make_project(mock_user.id)
        mock_db.query.return_value.filter.return_value.offset.return_value \
            .limit.return_value.all.return_value = [p]
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Project"


class TestGetProjectById:
    def test_found(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        p = _make_project(mock_user.id, id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = p
        resp = client.get(f"/api/projects/{pid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == str(pid)

    def test_not_found_returns_404(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/projects/{uuid.uuid4()}")
        assert resp.status_code == 404


class TestCreateProject:
    def test_creates_project_successfully(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        created = _make_project(mock_user.id, id=pid, title="New Project")
        mock_db.refresh = MagicMock(side_effect=lambda x: None)
        # create_project uses Form fields and calls db.refresh(db_project)
        # After add+commit+refresh, the returned object is db_project itself
        # We mock refresh to set attributes on the object passed to it
        def _refresh_side_effect(obj):
            obj.id = created.id
            obj.created_at = created.created_at

        mock_db.refresh.side_effect = _refresh_side_effect

        # Endpoint uses Form — must send as multipart data
        resp = client.post("/api/projects", data={
            "title": "New Project",
            "description": "Desc",
            "requirement_template": "ISO29148",
        })
        assert resp.status_code == 200
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_missing_title_returns_422(self, client):
        resp = client.post("/api/projects", data={"description": "No title"})
        assert resp.status_code == 422


class TestUpdateProject:
    def test_update_title(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        p = _make_project(mock_user.id, id=pid)
        updated = _make_project(mock_user.id, id=pid, title="Updated")

        # first() returns project on first call, updated project on second call
        mock_db.query.return_value.filter.return_value.first.side_effect = [p, updated]
        # .update() must return an int so `updated_rows > 1` comparison works
        mock_db.query.return_value.filter.return_value.update.return_value = 1

        # Endpoint uses Form for update too
        resp = client.put(f"/api/projects/{pid}", data={"title": "Updated"})
        assert resp.status_code == 200
        assert mock_db.commit.called

    def test_update_nonexistent_returns_404(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.put(f"/api/projects/{uuid.uuid4()}", data={"title": "X"})
        assert resp.status_code == 404


class TestDeleteProject:
    def test_delete_existing(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        p = _make_project(mock_user.id, id=pid)
        # delete endpoint calls .first() for: Project + 4 related tables
        calls = [p, None, None, None, None]
        mock_db.query.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None
        # .delete() must return an int for `deleted_rows > 1` comparison
        mock_db.query.return_value.filter.return_value.delete.return_value = 1
        resp = client.delete(f"/api/projects/{pid}")
        assert resp.status_code == 200
        assert mock_db.commit.called

    def test_delete_nonexistent_returns_404(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.delete(f"/api/projects/{uuid.uuid4()}")
        assert resp.status_code == 404
