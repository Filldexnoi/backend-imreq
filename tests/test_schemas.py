"""
Unit tests for Pydantic schemas (schemas.py) — pure validation, no DB.
"""
import uuid
import pytest
from pydantic import ValidationError

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schemas


class TestUserSchemas:
    def test_user_create_valid(self):
        u = schemas.UserCreate(
            email="alice@example.com",
            username="alice",
            password="secret123",
        )
        assert u.email == "alice@example.com"
        assert u.username == "alice"

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            schemas.UserCreate(email="not-an-email", username="x", password="y")

    def test_user_create_missing_password(self):
        with pytest.raises(ValidationError):
            schemas.UserCreate(email="a@b.com", username="x")


class TestProjectSchemas:
    def test_project_create_valid(self):
        p = schemas.ProjectCreate(
            title="My Project",
            description="Desc",
            requirement_template="ISO29148",
        )
        assert p.title == "My Project"
        assert p.requirement_template == "ISO29148"

    def test_project_create_missing_title(self):
        with pytest.raises(ValidationError):
            schemas.ProjectCreate(description="No title")

    def test_project_update_all_optional(self):
        """ProjectUpdate should allow partial updates (all fields optional)."""
        pu = schemas.ProjectUpdate()
        assert pu.title is None


class TestSelectedRequirementSchemas:
    def test_selected_req_base_valid(self):
        s = schemas.SelectedRequirementBase(
            req_id="REQ-001",
            module="Auth",
            requirement="The system shall authenticate users.",
        )
        assert s.req_id == "REQ-001"

    def test_selected_req_base_missing_req_id(self):
        with pytest.raises(ValidationError):
            schemas.SelectedRequirementBase(
                module="Auth",
                requirement="Missing req_id.",
            )

    def test_selected_req_upsert_valid(self):
        u = schemas.SelectedRequirementUpsert(
            delete_req_ids=["REQ-001", "REQ-002"],
            insert=[
                schemas.SelectedRequirementBase(
                    req_id="REQ-001",
                    module="Auth",
                    requirement="The system shall log in users.",
                )
            ],
        )
        assert len(u.delete_req_ids) == 2
        assert len(u.insert) == 1

    def test_selected_req_upsert_empty_delete_and_insert(self):
        """Empty lists are valid — means no-op."""
        u = schemas.SelectedRequirementUpsert(delete_req_ids=[], insert=[])
        assert u.delete_req_ids == []
        assert u.insert == []

    def test_selected_req_upsert_missing_fields(self):
        with pytest.raises(ValidationError):
            schemas.SelectedRequirementUpsert()  # both fields required
