"""
Unit tests for GeminiService pure logic — Gemini API calls are mocked.
Tests: criterion definitions, score parsing, improvement filtering, split detection.
"""
import pytest
from unittest.mock import MagicMock, patch, call
from collections import Counter

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Patch heavy imports before importing gemini_service ─────────────────────
import unittest.mock as _mock

_gensim_mock = _mock.MagicMock()
_torch_mock = _mock.MagicMock()
_sentence_mock = _mock.MagicMock()

with _mock.patch.dict("sys.modules", {
    "gensim": _gensim_mock,
    "gensim.models": _gensim_mock.models,
    "gensim.models.doc2vec": _gensim_mock.models.doc2vec,
    "torch": _torch_mock,
    "sentence_transformers": _sentence_mock,
    "openai": _mock.MagicMock(),
}):
    with _mock.patch("os.getenv", return_value="fake-api-key"):
        from services.gemini_service import GeminiService


@pytest.fixture
def svc():
    with patch("os.getenv", return_value="fake-key"), \
         patch("services.gemini_service.OpenAI"):
        return GeminiService()


# ---------------------------------------------------------------------------
# Static data / constants
# ---------------------------------------------------------------------------

class TestCriteriaConstants:
    def test_exactly_9_criteria(self, svc):
        assert len(svc.CRITERIA_NAMES) == 9

    def test_all_expected_criteria_present(self, svc):
        expected = {
            "Appropriate", "Complete", "Conforming", "Correct",
            "Feasible", "Necessary", "Singular", "Unambiguous", "Verifiable",
        }
        assert set(svc.CRITERIA_NAMES) == expected

    def test_criterion_meaning_covers_all_9(self, svc):
        for name in svc.CRITERIA_NAMES:
            assert name in svc.CRITERION_MEANING, f"Missing meaning for {name}"

    def test_ears_template_has_5_patterns(self, svc):
        ears = svc.TEMPLATE_DEFINITIONS["EARS"]["patterns"]
        for kw in ["Ubiquitous", "State-driven", "Event-driven", "Unwanted behavior", "Optional feature"]:
            assert kw in ears

    def test_iso29148_template_defined(self, svc):
        assert "ISO29148" in svc.TEMPLATE_DEFINITIONS

    def test_rules_by_criterion_keys_subset_of_criteria(self, svc):
        for k in svc.RULES_BY_CRITERION:
            assert k in svc.CRITERIA_NAMES


class TestCriterionInstructions:
    def test_all_criteria_have_instructions(self, svc):
        for name in svc.CRITERIA_NAMES:
            assert name in svc.CRITERION_INSTRUCTIONS, f"No instruction for {name}"

    def test_conforming_instruction_mentions_shall(self, svc):
        assert "shall" in svc.CRITERION_INSTRUCTIONS["Conforming"].lower()

    def test_singular_instruction_mentions_split(self, svc):
        instr = svc.CRITERION_INSTRUCTIONS["Singular"].lower()
        assert "split" in instr or "single" in instr


# ---------------------------------------------------------------------------
# _build_rules_reference
# ---------------------------------------------------------------------------

class TestBuildRulesReference:
    def test_returns_string(self, svc):
        result = svc._build_rules_reference("Unambiguous")
        assert isinstance(result, str)

    def test_unknown_criterion_returns_no_rules(self, svc):
        result = svc._build_rules_reference("NonExistentCriterion")
        assert result == ""

    def test_conforming_includes_shall_rule(self, svc):
        result = svc._build_rules_reference("Conforming")
        assert "Shall" in result or "shall" in result

    def test_verifiable_includes_measurable(self, svc):
        result = svc._build_rules_reference("Verifiable")
        assert "Measurable" in result or "measurable" in result


# ---------------------------------------------------------------------------
# _analyze_single_criterion (mocked Gemini response)
# ---------------------------------------------------------------------------

class TestAnalyzeSingleCriterion:
    def _mock_response(self, svc, json_text: str):
        """Make svc.client.chat.completions.create return json_text."""
        msg = MagicMock()
        msg.content = json_text
        choice = MagicMock()
        choice.message = msg
        mock_resp = MagicMock()
        mock_resp.choices = [choice]
        svc.client.chat.completions.create.return_value = mock_resp

    def test_pass_result(self, svc):
        self._mock_response(svc, '{"status": "PASS", "reason": "", "cited_rules": [], "detected_pattern": "ISO29148: Standard"}')
        result = svc._analyze_single_criterion(
            criterion="Conforming",
            requirement="The system shall authenticate users.",
            req_id="REQ-001",
            requirement_template="ISO29148",
            reference_context=None,
        )
        assert result["status"] == "PASS"
        assert result["reason"] == ""

    def test_fail_result_has_reason(self, svc):
        self._mock_response(svc, '{"status": "FAIL", "reason": "Uses will instead of shall.", "cited_rules": ["Modal Verb \'Shall\'"], "detected_pattern": "None"}')
        result = svc._analyze_single_criterion(
            criterion="Conforming",
            requirement="The system will login the user.",
            req_id="REQ-002",
            requirement_template="ISO29148",
            reference_context=None,
        )
        assert result["status"] == "FAIL"
        assert "shall" in result["reason"].lower() or "will" in result["reason"].lower()

    def test_cannot_determine(self, svc):
        self._mock_response(svc, '{"status": "CANNOT_DETERMINE", "reason": "No reference doc.", "cited_rules": [], "detected_pattern": "None"}')
        result = svc._analyze_single_criterion(
            criterion="Correct",
            requirement="The system shall handle payments.",
            req_id="REQ-003",
            requirement_template="ISO29148",
            reference_context=None,
        )
        assert result["status"] == "CANNOT_DETERMINE"

    def test_conforming_injects_template_name(self, svc):
        self._mock_response(svc, '{"status": "PASS", "reason": "", "cited_rules": [], "detected_pattern": "EARS: Event-driven"}')
        result = svc._analyze_single_criterion(
            criterion="Conforming",
            requirement="WHEN the user logs in, the system shall validate credentials.",
            req_id="REQ-004",
            requirement_template="EARS",
            reference_context=None,
        )
        assert result["status"] == "PASS"


# ---------------------------------------------------------------------------
# Suggestion filtering logic (tested via _generate_suggestion_for_requirement)
# ---------------------------------------------------------------------------

class TestSuggestionFiltering:
    """
    Tests for _generate_suggestion_for_requirement with mocked Gemini.
    Focuses on the logic that filters CANNOT_DETERMINE before generating.
    """

    def _setup_suggestion_mock(self, svc, response_json: str):
        msg = MagicMock()
        msg.content = response_json
        choice = MagicMock()
        choice.message = msg
        mock_resp = MagicMock()
        mock_resp.choices = [choice]
        svc.client.chat.completions.create.return_value = mock_resp

    def test_all_cannot_determine_returns_no_change(self, svc):
        """If every failure is CANNOT_DETERMINE, no suggestion should be generated."""
        evaluation = {
            "Correct": "[?] no reference doc",
            "Feasible": "[?] no reference doc",
            "Necessary": "[?] no reference doc",
        }
        result = svc._generate_suggestion_for_requirement(
            req_id="REQ-001",
            requirement="The system shall do something.",
            evaluation=evaluation,
            module="",
            requirement_template="ISO29148",
        )
        # Should return original unchanged
        assert result["suggested_requirement"] == "The system shall do something."
        assert result.get("is_split") is False or result.get("is_split") is None

    def test_singular_fail_triggers_split(self, svc):
        """Singular failure should produce a split, not a rewrite."""
        evaluation = {
            "Singular": "Requirement bundles two functions: login and logout.",
        }
        split_response = '''{
            "is_split": true,
            "split_requirements": [
                {"req_id": "REQ-001-1", "requirement": "The system shall authenticate users.", "explanation": "Split: login"},
                {"req_id": "REQ-001-2", "requirement": "The system shall log out users.", "explanation": "Split: logout"}
            ],
            "improvements": {"Singular": {"description": "Split into two requirements.", "cited_rules": []}}
        }'''
        self._setup_suggestion_mock(svc, split_response)
        result = svc._generate_suggestion_for_requirement(
            req_id="REQ-001",
            requirement="The system shall login and logout users.",
            evaluation=evaluation,
            module="",
            requirement_template="ISO29148",
        )
        assert result.get("is_split") is True
        assert len(result.get("split_requirements", [])) == 2
