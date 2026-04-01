"""
Tests for routers/analyze.py
- verify_project_ownership helper
- POST /api/analyze-parallel/projects/{project_id}/requirements
- POST /api/analyze-parallel/projects/{project_id}/requirements/{req_id} (single)
"""
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from routers.analyze import verify_project_ownership


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(**kw):
    p = MagicMock(spec=models.Project)
    p.id = kw.get("id", uuid.uuid4())
    p.user_id = kw.get("user_id", uuid.uuid4())
    p.requirement_template = kw.get("requirement_template", "ISO29148")
    p.reference_files = kw.get("reference_files", None)
    return p


def _make_origin_req(**kw):
    r = MagicMock(spec=models.OriginRequirement)
    r.id = kw.get("id", uuid.uuid4())
    r.req_id = kw.get("req_id", "REQ-001")
    r.module = kw.get("module", "Module A")
    r.requirement = kw.get("requirement", "The system shall do X.")
    r.project_id = kw.get("project_id", uuid.uuid4())
    return r


# ---------------------------------------------------------------------------
# verify_project_ownership (pure helper, no HTTP)
# ---------------------------------------------------------------------------

class TestVerifyProjectOwnership:
    def test_project_found(self):
        db = MagicMock()
        project = _make_project()
        db.query.return_value.filter.return_value.first.return_value = project
        result = verify_project_ownership(project.id, project.user_id, db)
        assert result == project

    def test_project_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(HTTPException) as exc_info:
            verify_project_ownership(uuid.uuid4(), uuid.uuid4(), db)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/analyze-parallel/projects/{project_id}/requirements
# ---------------------------------------------------------------------------

class TestAnalyzeProjectRequirementsParallel:
    def _fake_db_save(self):
        """Returns a MagicMock acting as a fresh DB session."""
        db_save = MagicMock()
        db_save.query.return_value.filter.return_value.delete.return_value = 0
        return db_save

    def test_analyze_success(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        req1 = _make_origin_req(req_id="REQ-001", project_id=pid)
        req2 = _make_origin_req(req_id="REQ-002", project_id=pid)

        # First .first() → project (verify_project_ownership)
        # Then .all() → [req1, req2]
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [req1, req2]

        fake_result = {
            "results": [
                {"req_id": "REQ-001", "score": "8/9", "evaluation": {}, "characteristics": []},
                {"req_id": "REQ-002", "score": "9/9", "evaluation": {}, "characteristics": []},
            ],
            "summary": {"passed": 1, "failed": 1}
        }
        db_save = self._fake_db_save()

        with patch("routers.analyze.gemini_service.analyze_requirements_parallel",
                   new_callable=AsyncMock, return_value=fake_result), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""), \
             patch("routers.analyze.get_db_with_retry", return_value=db_save):
            resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")

        assert resp.status_code == 200
        data = resp.json()
        assert data["analyzed_count"] == 2
        assert data["method"] == "detailed_parallel"

    def test_analyze_project_not_found(self, client, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.post(f"/api/analyze-parallel/projects/{uuid.uuid4()}/requirements")
        assert resp.status_code == 404

    def test_analyze_no_origin_requirements(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = []

        resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")
        assert resp.status_code == 404
        assert "No origin requirements found" in resp.json()["detail"]

    def test_analyze_with_duplicate_req_ids(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        req1 = _make_origin_req(req_id="REQ-001", project_id=pid)
        req1_dup = _make_origin_req(req_id="REQ-001", project_id=pid)  # duplicate

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [req1, req1_dup]

        fake_result = {
            "results": [
                {"req_id": "REQ-001", "score": "7/9", "evaluation": {}, "characteristics": []},
            ],
            "summary": {}
        }
        db_save = self._fake_db_save()

        with patch("routers.analyze.gemini_service.analyze_requirements_parallel",
                   new_callable=AsyncMock, return_value=fake_result), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""), \
             patch("routers.analyze.get_db_with_retry", return_value=db_save):
            resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")

        # Should succeed and deduplicate
        assert resp.status_code == 200
        assert resp.json()["analyzed_count"] == 1

    def test_analyze_service_exception_raises_500(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        req = _make_origin_req(project_id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [req]

        with patch("routers.analyze.gemini_service.analyze_requirements_parallel",
                   new_callable=AsyncMock, side_effect=Exception("API error")), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""):
            resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")

        assert resp.status_code == 500
        assert "Analysis failed" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# POST /api/analyze-parallel/projects/{project_id}/requirements/{req_id}
# ---------------------------------------------------------------------------

class TestAnalyzeSingleRequirementDetailed:
    def test_single_analyze_success(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        req_id = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        req = _make_origin_req(id=req_id, req_id="REQ-001", project_id=pid)

        # verify_project_ownership: .filter().first()
        mock_db.query.return_value.filter.return_value.first.return_value = project
        # origin_req: .filter().filter().first()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = req

        fake_analysis = {
            "score": "8/9",
            "evaluation": {"Appropriate": {"status": "PASS"}},
            "characteristics": ["clear"],
        }

        with patch("routers.analyze.gemini_service._analyze_single_requirement_all_criteria",
                   return_value=fake_analysis), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""):
            resp = client.post(
                f"/api/analyze-parallel/projects/{pid}/requirements/{req_id}"
            )

        assert resp.status_code == 200

    def test_single_analyze_project_not_found(self, client, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.post(
            f"/api/analyze-parallel/projects/{uuid.uuid4()}/requirements/{uuid.uuid4()}"
        )
        assert resp.status_code == 404

    def test_single_analyze_req_not_found(self, client, mock_db, mock_user):
        project = _make_project(user_id=mock_user.id)
        # verify_project_ownership: .filter().first() → project
        mock_db.query.return_value.filter.return_value.first.return_value = project
        # origin_req: .filter().filter().first() → None
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = None

        resp = client.post(
            f"/api/analyze-parallel/projects/{uuid.uuid4()}/requirements/{uuid.uuid4()}"
        )
        assert resp.status_code == 404
        assert "Requirement not found" in resp.json()["detail"]
