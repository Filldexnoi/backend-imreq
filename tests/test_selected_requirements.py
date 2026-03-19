"""
Tests for selected-requirement endpoints:
  POST   /api/projects/{id}/selectedrequirements  — bulk replace
  PATCH  /api/projects/{id}/selectedrequirements  — upsert single
  GET    /api/projects/{id}/selectedrequirements  — list
"""
import uuid
import pytest
from unittest.mock import MagicMock, call

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models


def _make_project(user_id):
    p = MagicMock(spec=models.Project)
    p.id = uuid.uuid4()
    p.user_id = user_id
    return p


def _project_found(mock_db, user_id):
    p = _make_project(user_id)
    mock_db.query.return_value.filter.return_value.first.return_value = p
    mock_db.query.return_value.filter.return_value.count.return_value = 0
    mock_db.query.return_value.filter.return_value.delete.return_value = None
    mock_db.query.return_value.filter.return_value.skip.return_value \
        .limit.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value \
        .offset.return_value.limit.return_value.all.return_value = []
    return p


def _project_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None


class TestPostSelectedRequirements:
    def test_bulk_insert_success(self, client, mock_db, mock_user):
        _project_found(mock_db, mock_user.id)
        pid = uuid.uuid4()
        payload = [
            {"req_id": "REQ-001", "module": "Auth", "requirement": "The system shall login."},
            {"req_id": "REQ-002", "module": "Auth", "requirement": "The system shall logout."},
        ]
        resp = client.post(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 200
        assert resp.json()["inserted"] == 2
        assert mock_db.bulk_save_objects.called
        assert mock_db.commit.called

    def test_bulk_insert_replaces_existing(self, client, mock_db, mock_user):
        """Existing records should be deleted before inserting new ones."""
        _project_found(mock_db, mock_user.id)
        # Simulate existing records
        mock_db.query.return_value.filter.return_value.count.return_value = 3
        pid = uuid.uuid4()
        payload = [{"req_id": "REQ-001", "module": "M", "requirement": "New req."}]
        resp = client.post(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 200
        # delete should have been called
        assert mock_db.query.return_value.filter.return_value.delete.called

    def test_project_not_found_returns_404(self, client, mock_db):
        _project_not_found(mock_db)
        pid = uuid.uuid4()
        payload = [{"req_id": "REQ-001", "module": "M", "requirement": "R."}]
        resp = client.post(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 404

    def test_empty_payload_inserts_zero(self, client, mock_db, mock_user):
        _project_found(mock_db, mock_user.id)
        pid = uuid.uuid4()
        resp = client.post(f"/api/projects/{pid}/selectedrequirements", json=[])
        assert resp.status_code == 200
        assert resp.json()["inserted"] == 0


class TestPatchSelectedRequirements:
    def test_upsert_single_normal_req(self, client, mock_db, mock_user):
        _project_found(mock_db, mock_user.id)
        mock_db.query.return_value.filter.return_value.filter.return_value \
            .delete.return_value = None
        pid = uuid.uuid4()
        payload = {
            "delete_req_ids": ["REQ-001"],
            "insert": [{"req_id": "REQ-001", "module": "Auth", "requirement": "The system shall login."}],
        }
        resp = client.patch(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] == 1
        assert data["inserted"] == 1

    def test_upsert_split_req(self, client, mock_db, mock_user):
        """Deletes original req_id and inserts multiple split entries."""
        _project_found(mock_db, mock_user.id)
        pid = uuid.uuid4()
        payload = {
            "delete_req_ids": ["REQ-010", "REQ-010-1", "REQ-010-2"],
            "insert": [
                {"req_id": "REQ-010-1", "module": "M", "requirement": "Part 1."},
                {"req_id": "REQ-010-2", "module": "M", "requirement": "Part 2."},
            ],
        }
        resp = client.patch(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 200
        assert resp.json()["deleted"] == 3
        assert resp.json()["inserted"] == 2

    def test_upsert_empty_insert_just_deletes(self, client, mock_db, mock_user):
        _project_found(mock_db, mock_user.id)
        pid = uuid.uuid4()
        payload = {"delete_req_ids": ["REQ-999"], "insert": []}
        resp = client.patch(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 200
        assert resp.json()["inserted"] == 0

    def test_upsert_project_not_found_returns_404(self, client, mock_db):
        _project_not_found(mock_db)
        pid = uuid.uuid4()
        payload = {"delete_req_ids": ["REQ-001"], "insert": []}
        resp = client.patch(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 404

    def test_upsert_empty_delete_ids_still_inserts(self, client, mock_db, mock_user):
        _project_found(mock_db, mock_user.id)
        pid = uuid.uuid4()
        payload = {
            "delete_req_ids": [],
            "insert": [{"req_id": "REQ-NEW", "module": "M", "requirement": "Brand new."}],
        }
        resp = client.patch(f"/api/projects/{pid}/selectedrequirements", json=payload)
        assert resp.status_code == 200
        assert resp.json()["inserted"] == 1


class TestGetSelectedRequirements:
    def test_returns_list(self, client, mock_db, mock_user):
        sr = MagicMock(spec=models.SelectedRequirement)
        sr.id = uuid.uuid4()
        sr.req_id = "REQ-001"
        sr.project_id = uuid.uuid4()
        sr.module = "Auth"
        sr.requirement = "The system shall login."
        sr.created_at = None
        sr.updated_at = None
        _project_found(mock_db, mock_user.id)
        mock_db.query.return_value.filter.return_value \
            .offset.return_value.limit.return_value.all.return_value = [sr]
        pid = uuid.uuid4()
        resp = client.get(f"/api/projects/{pid}/selectedrequirements")
        assert resp.status_code == 200

    def test_project_not_found_returns_404(self, client, mock_db):
        _project_not_found(mock_db)
        resp = client.get(f"/api/projects/{uuid.uuid4()}/selectedrequirements")
        assert resp.status_code == 404
