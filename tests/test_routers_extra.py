"""
Extra edge-case tests for routers/analyze.py and routers/suggestion.py
covering branches missed by previous tests.
"""
import uuid
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(user_id=None, **kw):
    p = MagicMock(spec=models.Project)
    p.id = kw.get("id", uuid.uuid4())
    p.user_id = user_id or uuid.uuid4()
    p.requirement_template = kw.get("requirement_template", "ISO29148")
    p.reference_files = kw.get("reference_files", None)
    p.created_at = datetime.now(timezone.utc)
    return p


def _make_origin_req(**kw):
    r = MagicMock(spec=models.OriginRequirement)
    r.id = kw.get("id", uuid.uuid4())
    r.req_id = kw.get("req_id", "REQ-001")
    r.module = kw.get("module", "Module A")
    r.requirement = kw.get("requirement", "The system shall do X.")
    return r


def _make_analyzed_req(**kw):
    r = MagicMock(spec=models.AnalyzedRequirement)
    r.id = kw.get("id", uuid.uuid4())
    r.req_id = kw.get("req_id", "REQ-001")
    r.module = kw.get("module", "Module A")
    r.requirement = kw.get("requirement", "The system shall do X.")
    r.score = kw.get("score", "7/9")
    r.evaluation = kw.get("evaluation", {"Appropriate": "FAIL"})
    r.characteristics = kw.get("characteristics", [])
    return r


def _make_suggestion(**kw):
    s = MagicMock(spec=models.SuggestedRequirement)
    s.id = kw.get("id", uuid.uuid4())
    s.project_id = kw.get("project_id", uuid.uuid4())
    s.req_id = kw.get("req_id", "REQ-001")
    s.module = kw.get("module", "M")
    s.original_requirement = kw.get("original_requirement", "Original.")
    s.suggested_requirement = kw.get("suggested_requirement", "Suggested.")
    s.original_score = kw.get("original_score", "7/9")
    s.improvements = kw.get("improvements", {})
    s.is_split = kw.get("is_split", False)
    s.split_requirements = kw.get("split_requirements", None)
    s.created_at = kw.get("created_at", datetime.now(timezone.utc))
    return s


# ===========================================================================
# routers/analyze.py extra branches
# ===========================================================================

class TestAnalyzeSingleReqUpdateExisting:
    """Covers the 'update existing analyzed requirement' branch (line 256-263)."""

    def test_single_analyze_updates_existing(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        req_uuid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        origin_req = _make_origin_req(id=req_uuid, req_id="REQ-001")
        existing_analyzed = _make_analyzed_req(req_id="REQ-001")

        # verify_project_ownership: .filter().first() → project
        mock_db.query.return_value.filter.return_value.first.return_value = project
        # origin_req: .filter().filter().first() → origin_req
        # existing analyzed: same chain level but different query
        calls = [origin_req, existing_analyzed]
        mock_db.query.return_value.filter.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None

        fake_analysis = {
            "score": "8/9",
            "evaluation": {},
            "characteristics": ["Appropriate", "Complete"],
            "detailed_results": [],
        }
        with patch("routers.analyze.gemini_service._analyze_single_requirement_all_criteria",
                   return_value=fake_analysis), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""):
            resp = client.post(
                f"/api/analyze-parallel/projects/{pid}/requirements/{req_uuid}"
            )
        assert resp.status_code == 200
        assert mock_db.commit.called

    def test_single_analyze_creates_new(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        req_uuid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        origin_req = _make_origin_req(id=req_uuid, req_id="REQ-001")
        new_analyzed = _make_analyzed_req(req_id="REQ-001")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        calls = [origin_req, None]  # origin found, no existing analyzed
        mock_db.query.return_value.filter.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None
        mock_db.refresh.side_effect = lambda obj: None

        fake_analysis = {
            "score": "7/9",
            "evaluation": {"Unambiguous": {"reason": "vague", "cited_rules": []}},
            "characteristics": ["Appropriate"],
            "detailed_results": [],
        }
        with patch("routers.analyze.gemini_service._analyze_single_requirement_all_criteria",
                   return_value=fake_analysis), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""):
            with patch("routers.analyze.models.AnalyzedRequirement", return_value=new_analyzed):
                resp = client.post(
                    f"/api/analyze-parallel/projects/{pid}/requirements/{req_uuid}"
                )
        assert resp.status_code == 200
        assert mock_db.add.called

    def test_single_analyze_service_exception_500(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        req_uuid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        origin_req = _make_origin_req(id=req_uuid, req_id="REQ-001")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.filter.return_value.first.return_value = origin_req

        with patch("routers.analyze.gemini_service._analyze_single_requirement_all_criteria",
                   side_effect=Exception("LLM error")), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""):
            resp = client.post(
                f"/api/analyze-parallel/projects/{pid}/requirements/{req_uuid}"
            )
        assert resp.status_code == 500
        assert "Analysis failed" in resp.json()["detail"]


# ===========================================================================
# routers/analyze.py — save_failed branch in parallel analyze
# ===========================================================================

class TestAnalyzeParallelSaveFailed:
    def test_save_exception_raises_500(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        req = _make_origin_req(project_id=pid)

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [req]

        fake_result = {
            "results": [{"req_id": "REQ-001", "score": "7/9", "evaluation": {}, "characteristics": []}],
            "summary": {}
        }
        db_save = MagicMock()
        db_save.query.return_value.filter.return_value.delete.return_value = 0
        db_save.commit.side_effect = Exception("DB commit failed")

        with patch("routers.analyze.gemini_service.analyze_requirements_parallel",
                   new_callable=AsyncMock, return_value=fake_result), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""), \
             patch("routers.analyze.get_db_with_retry", return_value=db_save):
            resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")
        assert resp.status_code == 500


# ===========================================================================
# routers/suggestion.py extra branches
# ===========================================================================

class TestSuggestionGenerateFailed:
    """Covers line 107-108: failed suggestion in generate_suggestions_for_project."""

    def test_generate_skips_failed_suggestion(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        analyzed = _make_analyzed_req(req_id="REQ-001")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [analyzed]
        mock_db.query.return_value.filter.return_value.delete.return_value = 0

        # One failed suggestion (success=False)
        fake_result = {
            "results": [{"req_id": "REQ-001", "success": False, "error": "LLM failed"}],
            "summary": {}
        }
        with patch("routers.suggestion.suggestion_service.generate_suggestions_parallel",
                   new_callable=AsyncMock, return_value=fake_result):
            resp = client.post(f"/api/suggestions/projects/{pid}/generate")

        assert resp.status_code == 200
        assert resp.json()["saved_count"] == 0

    def test_generate_exception_raises_500(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(id=pid, user_id=mock_user.id)
        analyzed = _make_analyzed_req(req_id="REQ-001")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [analyzed]

        with patch("routers.suggestion.suggestion_service.generate_suggestions_parallel",
                   new_callable=AsyncMock, side_effect=Exception("LLM down")):
            resp = client.post(f"/api/suggestions/projects/{pid}/generate")

        assert resp.status_code == 500
        assert "Suggestion generation failed" in resp.json()["detail"]


class TestSuggestionGenerateSingleUpdateExisting:
    """Covers line 218-225: update existing suggestion branch."""

    def test_update_existing_suggestion(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        analyzed = _make_analyzed_req(req_id="REQ-001", score="5/9")
        existing_sug = _make_suggestion(req_id="REQ-001")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        calls = [analyzed, existing_sug]  # analyzed_req then existing suggestion
        mock_db.query.return_value.filter.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None

        fake_result = {
            "success": True,
            "suggested_requirement": "Updated req.",
            "improvements": {},
            "is_split": False,
            "split_requirements": None,
            "explanation": "Updated."
        }
        with patch("routers.suggestion.suggestion_service._generate_suggestion_for_requirement",
                   return_value=fake_result):
            resp = client.post(
                f"/api/suggestions/projects/{pid}/requirements/REQ-001/generate"
            )
        assert resp.status_code == 200
        assert mock_db.commit.called

    def test_generate_single_failure_raises_500(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        analyzed = _make_analyzed_req(req_id="REQ-001", score="5/9")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.filter.return_value.first.side_effect = \
            [analyzed, None]

        fake_result = {
            "success": False,
            "error": "LLM error"
        }
        with patch("routers.suggestion.suggestion_service._generate_suggestion_for_requirement",
                   return_value=fake_result):
            resp = client.post(
                f"/api/suggestions/projects/{pid}/requirements/REQ-001/generate"
            )
        assert resp.status_code == 500

    def test_generate_single_exception_raises_500(self, client, mock_db):
        pid = uuid.uuid4()
        project = _make_project(id=pid)
        analyzed = _make_analyzed_req(req_id="REQ-001", score="5/9")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        calls = [analyzed, None]
        mock_db.query.return_value.filter.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None

        with patch("routers.suggestion.suggestion_service._generate_suggestion_for_requirement",
                   side_effect=Exception("Unexpected error")):
            resp = client.post(
                f"/api/suggestions/projects/{pid}/requirements/REQ-001/generate"
            )
        assert resp.status_code == 500


# ===========================================================================
# routers/analyze.py parallel — characteristics as string/non-list (line 146-154)
# ===========================================================================

class TestAnalyzeParallelCharacteristicsEdgeCases:
    def _setup(self, mock_db, mock_user, pid):
        project = _make_project(id=pid, user_id=mock_user.id)
        req = _make_origin_req(req_id="REQ-001", project_id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value.all.return_value = [req]
        return req

    def test_characteristics_as_json_string(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        self._setup(mock_db, mock_user, pid)
        fake_result = {
            "results": [{
                "req_id": "REQ-001",
                "score": "2/9",
                "evaluation": {},
                "characteristics": '["Appropriate", "Complete"]'  # JSON string
            }],
            "summary": {}
        }
        db_save = MagicMock()
        db_save.query.return_value.filter.return_value.delete.return_value = 0
        with patch("routers.analyze.gemini_service.analyze_requirements_parallel",
                   new_callable=AsyncMock, return_value=fake_result), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""), \
             patch("routers.analyze.get_db_with_retry", return_value=db_save):
            resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")
        assert resp.status_code == 200

    def test_characteristics_as_invalid_string(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        self._setup(mock_db, mock_user, pid)
        fake_result = {
            "results": [{
                "req_id": "REQ-001",
                "score": "1/9",
                "evaluation": {},
                "characteristics": "not_valid_json{"  # invalid JSON string
            }],
            "summary": {}
        }
        db_save = MagicMock()
        db_save.query.return_value.filter.return_value.delete.return_value = 0
        with patch("routers.analyze.gemini_service.analyze_requirements_parallel",
                   new_callable=AsyncMock, return_value=fake_result), \
             patch("routers.analyze.gemini_service._extract_reference_text", return_value=""), \
             patch("routers.analyze.get_db_with_retry", return_value=db_save):
            resp = client.post(f"/api/analyze-parallel/projects/{pid}/requirements")
        assert resp.status_code == 200
