"""
Tests for routers/suggestion.py
- filter_improvements_by_evaluation (pure function)
- GET/DELETE suggestions endpoints
- POST generate suggestions (mocked GeminiService)
- POST generate single requirement suggestion
"""
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from routers.suggestion import filter_improvements_by_evaluation


# ---------------------------------------------------------------------------
# Pure function tests
# ---------------------------------------------------------------------------

class TestFilterImprovementsByEvaluation:
    def test_empty_inputs(self):
        assert filter_improvements_by_evaluation({}, {}) == {}

    def test_none_evaluation(self):
        assert filter_improvements_by_evaluation({"Appropriate": "Fix A"}, None) == {}

    def test_none_improvements(self):
        assert filter_improvements_by_evaluation(None, {"Appropriate": "fail"}) == {}

    def test_keeps_failed_criteria(self):
        improvements = {
            "Appropriate": "Fix wording",
            "Complete": "Add more detail",
            "Verifiable": "Add metrics",
        }
        evaluation = {"Appropriate": "FAIL reason", "Verifiable": "FAIL reason"}
        result = filter_improvements_by_evaluation(improvements, evaluation)
        assert "Appropriate" in result
        assert "Verifiable" in result
        assert "Complete" not in result  # not in evaluation (passed)

    def test_excludes_error_key(self):
        improvements = {"Appropriate": "Fix it", "error": "some error"}
        evaluation = {"Appropriate": "FAIL", "error": "err"}
        result = filter_improvements_by_evaluation(improvements, evaluation)
        assert "Appropriate" in result
        assert "error" not in result

    def test_no_failed_criteria(self):
        improvements = {"Appropriate": "Fix it"}
        evaluation = {"Complete": "FAIL reason"}  # different criterion
        result = filter_improvements_by_evaluation(improvements, evaluation)
        assert result == {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(**kw):
    p = MagicMock(spec=models.Project)
    p.id = kw.get("id", uuid.uuid4())
    p.requirement_template = kw.get("requirement_template", "ISO29148")
    return p


def _make_analyzed_req(**kw):
    r = MagicMock(spec=models.AnalyzedRequirement)
    r.id = kw.get("id", uuid.uuid4())
    r.req_id = kw.get("req_id", "REQ-001")
    r.module = kw.get("module", "Module A")
    r.requirement = kw.get("requirement", "The system shall do X.")
    r.score = kw.get("score", "7/9")
    r.evaluation = kw.get("evaluation", {"Appropriate": "FAIL"})
    return r


def _make_suggestion(**kw):
    s = MagicMock(spec=models.SuggestedRequirement)
    s.id = kw.get("id", uuid.uuid4())
    s.req_id = kw.get("req_id", "REQ-001")
    s.module = kw.get("module", "Module A")
    s.original_requirement = kw.get("original_requirement", "Original req.")
    s.suggested_requirement = kw.get("suggested_requirement", "Suggested req.")
    s.original_score = kw.get("original_score", "7/9")
    s.improvements = kw.get("improvements", {})
    s.created_at = kw.get("created_at", datetime.utcnow())
    return s


# ---------------------------------------------------------------------------
# GET /api/suggestions/projects/{project_id}
# ---------------------------------------------------------------------------

class TestGetSuggestionsForProject:
    def test_returns_suggestions(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        s = _make_suggestion(req_id="REQ-001")
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .offset.return_value.limit.return_value.all.return_value = [s]

        resp = client.get(f"/api/suggestions/projects/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["suggestions"][0]["req_id"] == "REQ-001"

    def test_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/suggestions/projects/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_empty_suggestions(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .offset.return_value.limit.return_value.all.return_value = []

        resp = client.get(f"/api/suggestions/projects/{pid}")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


# ---------------------------------------------------------------------------
# GET /api/suggestions/projects/{project_id}/requirements/{req_id}
# ---------------------------------------------------------------------------

class TestGetSuggestionForRequirement:
    def test_found(self, client, mock_db):
        s = _make_suggestion(req_id="REQ-001")
        mock_db.query.return_value.filter.return_value \
            .filter.return_value.first.return_value = s

        resp = client.get(f"/api/suggestions/projects/{uuid.uuid4()}/requirements/REQ-001")
        assert resp.status_code == 200
        assert resp.json()["req_id"] == "REQ-001"

    def test_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value \
            .filter.return_value.first.return_value = None

        resp = client.get(f"/api/suggestions/projects/{uuid.uuid4()}/requirements/REQ-999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/suggestions/projects/{project_id}
# ---------------------------------------------------------------------------

class TestDeleteSuggestions:
    def test_delete_returns_count(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.delete.return_value = 5

        resp = client.delete(f"/api/suggestions/projects/{uuid.uuid4()}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted_count"] == 5
        assert mock_db.commit.called

    def test_delete_zero(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        resp = client.delete(f"/api/suggestions/projects/{uuid.uuid4()}")
        assert resp.status_code == 200
        assert resp.json()["deleted_count"] == 0


# ---------------------------------------------------------------------------
# POST /api/suggestions/projects/{project_id}/generate
# ---------------------------------------------------------------------------

class TestGenerateSuggestionsForProject:
    def test_generate_success(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        analyzed = _make_analyzed_req(req_id="REQ-001")

        # verify_project_ownership
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [analyzed]
        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        fake_result = {
            "results": [{
                "req_id": "REQ-001",
                "success": True,
                "suggested_requirement": "The system shall do X properly.",
                "improvements": {"Appropriate": "Better wording"},
                "is_split": False,
                "split_requirements": None,
            }],
            "summary": {}
        }

        with patch("routers.suggestion.suggestion_service.generate_suggestions_parallel",
                   new_callable=AsyncMock, return_value=fake_result):
            resp = client.post(f"/api/suggestions/projects/{pid}/generate")

        assert resp.status_code == 200
        data = resp.json()
        assert data["saved_count"] == 1

    def test_generate_no_analyzed_requirements(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = []

        resp = client.post(f"/api/suggestions/projects/{pid}/generate")
        assert resp.status_code == 404
        assert "No analyzed requirements" in resp.json()["detail"]

    def test_generate_project_not_found(self, client, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.post(f"/api/suggestions/projects/{uuid.uuid4()}/generate")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/suggestions/projects/{project_id}/requirements/{req_id}/generate
# ---------------------------------------------------------------------------

class TestGenerateSingleSuggestion:
    def test_perfect_score_skipped(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        analyzed = _make_analyzed_req(req_id="REQ-001", score="9/9")

        # project: .filter().first()
        mock_db.query.return_value.filter.return_value.first.return_value = project
        # analyzed_req: .filter().filter().first()
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = analyzed

        resp = client.post(f"/api/suggestions/projects/{pid}/requirements/REQ-001/generate")
        assert resp.status_code == 200
        assert resp.json()["suggestion_needed"] is False

    def test_generate_single_success(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        analyzed = _make_analyzed_req(req_id="REQ-001", score="5/9")

        # project: .filter().first()
        # analyzed_req: .filter().filter().first() (chained)
        # existing_suggestion: .filter().filter().first() → None (no existing)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        calls = [analyzed, None]
        mock_db.query.return_value.filter.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None

        fake_result = {
            "success": True,
            "suggested_requirement": "Improved req.",
            "improvements": {"Appropriate": "Fix wording"},
            "is_split": False,
            "split_requirements": None,
            "explanation": "Improved wording."
        }

        with patch("routers.suggestion.suggestion_service._generate_suggestion_for_requirement",
                   return_value=fake_result):
            resp = client.post(
                f"/api/suggestions/projects/{pid}/requirements/REQ-001/generate"
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["req_id"] == "REQ-001"
        assert "suggested_requirement" in data

    def test_generate_single_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.post(
            f"/api/suggestions/projects/{uuid.uuid4()}/requirements/REQ-001/generate"
        )
        assert resp.status_code == 404

    def test_generate_single_analyzed_req_not_found(self, client, mock_db):
        project = _make_project()
        # project: .filter().first()
        mock_db.query.return_value.filter.return_value.first.return_value = project
        # analyzed_req: .filter().filter().first() → None
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = None

        resp = client.post(
            f"/api/suggestions/projects/{uuid.uuid4()}/requirements/REQ-999/generate"
        )
        assert resp.status_code == 404
