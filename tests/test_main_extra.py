"""
Additional tests for main.py endpoints not covered elsewhere:
- GET /
- GET/POST /api/projects/{project_id}/originrequirements
- GET /api/projects/{project_id}/reference-files/{index}
- GET /api/projects/{project_id}/suggestedrequirements (analyzed)
- GET /api/projects/{project_id}/suggestedrequirements/similarity (mocked gensim)
"""
import uuid
import pytest
import base64
from unittest.mock import MagicMock, patch
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
    p.title = kw.get("title", "Test Project")
    p.description = kw.get("description", "Desc")
    p.requirement_template = kw.get("requirement_template", "ISO29148")
    p.reference_files = kw.get("reference_files", None)
    p.created_at = kw.get("created_at", datetime.now(timezone.utc))
    p.updated_at = kw.get("updated_at", None)
    return p


def _make_origin_req(**kw):
    r = MagicMock(spec=models.OriginRequirement)
    r.id = kw.get("id", uuid.uuid4())
    r.req_id = kw.get("req_id", "REQ-001")
    r.module = kw.get("module", "Module A")
    r.requirement = kw.get("requirement", "System shall do X.")
    r.project_id = kw.get("project_id", uuid.uuid4())
    r.created_at = kw.get("created_at", datetime.now(timezone.utc))
    r.characteristics = kw.get("characteristics", [])
    r.score = kw.get("score", None)
    r.evaluation = kw.get("evaluation", None)
    return r


def _make_suggestion(project_id=None, **kw):
    s = MagicMock(spec=models.SuggestedRequirement)
    s.id = kw.get("id", uuid.uuid4())
    s.project_id = project_id or uuid.uuid4()
    s.req_id = kw.get("req_id", "REQ-001")
    s.module = kw.get("module", "Module A")
    s.original_requirement = kw.get("original_requirement", "Original.")
    s.suggested_requirement = kw.get("suggested_requirement", "Suggested.")
    s.original_score = kw.get("original_score", "7/9")
    s.improvements = kw.get("improvements", {})
    s.is_split = kw.get("is_split", False)
    s.split_requirements = kw.get("split_requirements", None)
    s.created_at = kw.get("created_at", datetime.now(timezone.utc))
    return s


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestRootEndpoint:
    def test_root_returns_welcome(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "message" in resp.json()


# ---------------------------------------------------------------------------
# GET /api/projects/{project_id}/originrequirements
# ---------------------------------------------------------------------------

class TestGetOriginRequirements:
    def test_returns_requirements(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(user_id=mock_user.id, id=pid)
        req = _make_origin_req(project_id=pid)

        calls = [project]
        mock_db.query.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.offset.return_value.limit.return_value.all.return_value = [req]

        resp = client.get(f"/api/projects/{pid}/originrequirements")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/projects/{uuid.uuid4()}/originrequirements")
        assert resp.status_code == 404

    def test_empty_requirements(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(user_id=mock_user.id, id=pid)
        calls = [project]
        mock_db.query.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        resp = client.get(f"/api/projects/{pid}/originrequirements")
        assert resp.status_code == 200
        assert resp.json() == []


# ---------------------------------------------------------------------------
# GET /api/projects/{project_id}/reference-files/{file_index}
# ---------------------------------------------------------------------------

class TestDownloadReferenceFile:
    def test_download_success(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        content_bytes = b"PDF content here"
        encoded = base64.b64encode(content_bytes).decode("utf-8")
        file_data = [{"name": "doc.pdf", "content": encoded, "type": "application/pdf"}]
        project = _make_project(user_id=mock_user.id, id=pid, reference_files=file_data)
        mock_db.query.return_value.filter.return_value.first.return_value = project

        resp = client.get(f"/api/projects/{pid}/reference-files/0")
        assert resp.status_code == 200
        assert resp.content == content_bytes

    def test_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/projects/{uuid.uuid4()}/reference-files/0")
        assert resp.status_code == 404

    def test_no_reference_files(self, client, mock_db, mock_user):
        project = _make_project(user_id=mock_user.id, reference_files=None)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        resp = client.get(f"/api/projects/{uuid.uuid4()}/reference-files/0")
        assert resp.status_code == 404

    def test_file_index_out_of_range(self, client, mock_db, mock_user):
        content_bytes = b"data"
        encoded = base64.b64encode(content_bytes).decode("utf-8")
        file_data = [{"name": "doc.pdf", "content": encoded, "type": "application/pdf"}]
        project = _make_project(user_id=mock_user.id, reference_files=file_data)
        mock_db.query.return_value.filter.return_value.first.return_value = project

        resp = client.get(f"/api/projects/{uuid.uuid4()}/reference-files/99")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/projects/{project_id}/suggestedrequirements
# ---------------------------------------------------------------------------

class TestGetSuggestedRequirements:
    def test_returns_suggestions(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(user_id=mock_user.id, id=pid)
        s = _make_suggestion(project_id=pid, req_id="REQ-001")

        calls = [project]
        mock_db.query.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.offset.return_value.limit.return_value.all.return_value = [s]

        resp = client.get(f"/api/projects/{pid}/suggestedrequirements")
        assert resp.status_code == 200

    def test_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/projects/{uuid.uuid4()}/suggestedrequirements")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/projects/{project_id}/analyzedrequirements
# ---------------------------------------------------------------------------

class TestGetAnalyzedRequirements:
    def test_returns_analyzed(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(user_id=mock_user.id, id=pid)
        req = _make_origin_req(project_id=pid)

        calls = [project]
        mock_db.query.return_value.filter.return_value.first.side_effect = \
            lambda: calls.pop(0) if calls else None
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.offset.return_value.limit.return_value.all.return_value = [req]

        resp = client.get(f"/api/projects/{pid}/analyzedrequirements")
        assert resp.status_code == 200

    def test_project_not_found(self, client, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/projects/{uuid.uuid4()}/analyzedrequirements")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/projects/{project_id}/suggestedrequirements/similarity
# ---------------------------------------------------------------------------

class TestSimilarityEndpoint:
    def _setup_similarity_mocks(self, mock_db, mock_user, pid):
        project = _make_project(user_id=mock_user.id, id=pid)
        s1 = _make_suggestion(req_id="REQ-001", original_requirement="System shall A.",
                               suggested_requirement="System shall A properly.")
        s2 = _make_suggestion(req_id="REQ-002", original_requirement="System shall B.",
                               suggested_requirement="System shall B in real time.")

        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.all.return_value = [s1, s2]
        return project, [s1, s2]

    def test_similarity_project_not_found(self, client, mock_db, mock_user):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = client.get(f"/api/projects/{uuid.uuid4()}/suggestedrequirements/similarity")
        assert resp.status_code == 404

    def test_similarity_no_suggestions(self, client, mock_db, mock_user):
        pid = uuid.uuid4()
        project = _make_project(user_id=mock_user.id, id=pid)
        mock_db.query.return_value.filter.return_value.first.return_value = project
        mock_db.query.return_value.filter.return_value \
            .order_by.return_value.all.return_value = []

        resp = client.get(f"/api/projects/{pid}/suggestedrequirements/similarity")
        assert resp.status_code == 404
        assert "No suggested requirements" in resp.json()["detail"]

    def test_similarity_success(self, client, mock_db, mock_user):
        """English text → Doc2Vec path; Thai text → SBERT path."""
        import numpy as np
        pid = uuid.uuid4()
        self._setup_similarity_mocks(mock_db, mock_user, pid)

        # English pairs → Doc2Vec mock
        fake_vec = np.random.rand(40).astype(np.float32)
        mock_d2v_model = MagicMock()
        mock_d2v_model.infer_vector.return_value = fake_vec
        mock_d2v_model.corpus_count = 4
        mock_d2v_model.epochs = 60

        with patch("main.cosine_sim", return_value=np.array([[0.85]])), \
             patch("main.np.mean", return_value=np.float64(0.8)), \
             patch("main.np.median", return_value=np.float64(0.8)), \
             patch("main.np.min", return_value=np.float64(0.7)), \
             patch("main.np.max", return_value=np.float64(0.9)), \
             patch("main.np.argmin", return_value=0), \
             patch("main.np.argmax", return_value=1), \
             patch("gensim.models.doc2vec.TaggedDocument", side_effect=lambda tok, tag: MagicMock()), \
             patch("gensim.models.doc2vec.Doc2Vec", return_value=mock_d2v_model):
            resp = client.get(f"/api/projects/{pid}/suggestedrequirements/similarity")

        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "pairs" in data
        assert len(data["pairs"]) == 2
