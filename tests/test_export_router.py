"""
Tests for routers/export.py — CSV export endpoint.
"""
import uuid
import pytest
from unittest.mock import MagicMock
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models


def _make_project(**kw):
    p = MagicMock(spec=models.Project)
    p.id = kw.get("id", uuid.uuid4())
    p.title = kw.get("title", "My Project")
    return p


def _make_sel_req(**kw):
    r = MagicMock(spec=models.SelectedRequirement)
    r.req_id = kw.get("req_id", "REQ-001")
    r.module = kw.get("module", "Module A")
    r.requirement = kw.get("requirement", "The system shall do X.")
    return r


class TestExportCSV:
    def test_export_success(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid, title="Test Export")
        req1 = _make_sel_req(req_id="REQ-001", module="M1", requirement="System shall A.")
        req2 = _make_sel_req(req_id="REQ-002", module=None, requirement="System shall B.")

        # first() → project, then .all() → [req1, req2]
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.all.return_value = [req1, req2]

        resp = client.get(f"/api/export/projects/{pid}/selectedrequirements/csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        content = resp.text
        assert "req_id" in content
        assert "REQ-001" in content
        assert "REQ-002" in content
        assert "System shall A." in content

    def test_export_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/export/projects/{uuid.uuid4()}/selectedrequirements/csv")
        assert resp.status_code == 404
        assert "Project not found" in resp.json()["detail"]

    def test_export_no_selected_requirements(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.all.return_value = []

        resp = client.get(f"/api/export/projects/{pid}/selectedrequirements/csv")
        assert resp.status_code == 404
        assert "No selected requirements found" in resp.json()["detail"]

    def test_export_filename_in_header(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid, title="My Cool Project")
        req = _make_sel_req()
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.all.return_value = [req]

        resp = client.get(f"/api/export/projects/{pid}/selectedrequirements/csv")
        assert resp.status_code == 200
        assert "Content-Disposition" in resp.headers
        assert "attachment" in resp.headers["Content-Disposition"]

    def test_export_csv_has_correct_columns(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        req = _make_sel_req(req_id="REQ-100", module="CoreModule", requirement="Shall handle X.")
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.all.return_value = [req]

        resp = client.get(f"/api/export/projects/{pid}/selectedrequirements/csv")
        lines = resp.text.strip().split("\n")
        header = lines[0]
        assert "req_id" in header
        assert "module" in header
        assert "requirement" in header
