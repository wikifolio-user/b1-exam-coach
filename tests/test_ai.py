import json
import sys
from types import SimpleNamespace

import pytest

from services import ai_service
from services.writing_service import SCORE_NAMES


TASK = {"kind": "Email", "title": "Reply", "prompt": "Reply about your trip.",
        "points": ["Say when"], "keywords": [["Saturday"]], "starter": ""}
TEXT = "Hi Alex, we can travel on Saturday because I have no class. Best wishes, Sam"


def valid_payload():
    return {
        "scores": dict(zip(SCORE_NAMES, [4, 3.5, 3, 2.5])),
        "strengths": ["The date is clear."],
        "improvements": ["Add a reason for your choice."],
        "missing_points": [],
        "useful_phrases": ["Thanks for your email."],
        "exam_tip": "Write about 100 words.",
        "improved_version": "Hi Alex, we can travel on Saturday because I have no class. Best wishes, Sam",
    }


def test_ai_is_never_requested_without_explicit_opt_in(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "secret-test-key")
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: pytest.fail("Unexpected AI call"))
    feedback = ai_service.evaluate_writing(TEXT, TASK)
    assert feedback["provider"] == "offline"
    assert "fallback_reason" not in feedback


def test_missing_key_returns_actionable_offline_feedback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: pytest.fail("Unexpected AI call"))
    feedback = ai_service.evaluate_writing(TEXT, TASK, use_ai=True)
    assert feedback["provider"] == "offline"
    assert "No API key" in feedback["fallback_reason"]
    assert feedback["improved_version"] == ""


@pytest.mark.parametrize("key_source", ["environment", "argument"])
def test_success_validates_response_and_computes_word_count_and_total(monkeypatch, key_source):
    calls = []
    payload = valid_payload()
    payload.update({"provider": "untrusted", "word_count": 999, "total": 999, "private_metadata": "discard this"})
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: calls.append(args) or json.dumps(payload))
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    key = None if key_source == "environment" else "argument-key"
    feedback = ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key=key, model="gpt-4.1-mini")
    assert calls == [(TEXT, TASK, "env-key" if key is None else key, "gpt-4.1-mini")]
    assert feedback["provider"] == "openai"
    assert feedback["total"] == 13
    assert feedback["word_count"] != 999
    assert "private_metadata" not in feedback
    assert "official Cambridge" in feedback["disclaimer"]


def test_blank_explicit_key_does_not_silently_use_environment_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: pytest.fail("Unexpected AI call"))
    assert ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key=" ")["provider"] == "offline"


def test_api_failure_does_not_disclose_exception_or_credentials(monkeypatch):
    def failed_request(*args):
        raise RuntimeError("Authorization failed for secret-test-key; private provider error")
    monkeypatch.setattr(ai_service, "_request_feedback", failed_request)
    feedback = ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key="secret-test-key")
    assert feedback["provider"] == "offline"
    assert feedback["fallback_reason"] == "AI feedback is unavailable. Offline feedback is shown."
    assert "secret-test-key" not in repr(feedback)
    assert "private provider error" not in repr(feedback)


@pytest.mark.parametrize("raw", ["not JSON", "[]", "null", "{}", None, '{"scores": {}}'])
def test_malformed_api_output_falls_back(monkeypatch, raw):
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: raw)
    feedback = ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key="test-key")
    assert feedback["provider"] == "offline"
    assert "unavailable" in feedback["fallback_reason"]


@pytest.mark.parametrize("score", [-0.1, 5.1, "4", True, None, float("nan"), float("inf"), -float("inf")])
def test_out_of_range_non_numeric_or_non_finite_score_falls_back(monkeypatch, score):
    payload = valid_payload()
    payload["scores"]["Language"] = score
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: json.dumps(payload))
    assert ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key="test-key")["provider"] == "offline"


@pytest.mark.parametrize("field,value", [
    ("strengths", "A string is not a list"), ("improvements", [123]),
    ("missing_points", [None]), ("useful_phrases", {}),
    ("exam_tip", None), ("improved_version", ["Not a string"]),
])
def test_incorrect_feedback_types_fall_back(monkeypatch, field, value):
    payload = valid_payload()
    payload[field] = value
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: json.dumps(payload))
    assert ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key="test-key")["provider"] == "offline"


@pytest.mark.parametrize("scores", [{"Language": 3}, {**dict.fromkeys(SCORE_NAMES, 3), "Other": 2}, [3, 3, 3, 3]])
def test_rubric_must_contain_exactly_four_score_fields(monkeypatch, scores):
    payload = valid_payload()
    payload["scores"] = scores
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: json.dumps(payload))
    assert ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key="test-key")["provider"] == "offline"


@pytest.mark.parametrize("text", ["", "   ", "x" * 12001])
def test_empty_or_oversized_text_is_not_sent_to_ai(monkeypatch, text):
    monkeypatch.setattr(ai_service, "_request_feedback", lambda *args: pytest.fail("Unexpected AI call"))
    feedback = ai_service.evaluate_writing(text, TASK, use_ai=True, api_key="test-key")
    assert feedback["provider"] == "offline"
    assert feedback["fallback_reason"]


def test_client_boundary_uses_json_rubric_timeout_bounded_retries_and_closes(monkeypatch):
    constructor_args = []
    request_args = []
    closed = []
    class FakeClient:
        def __init__(self, **kwargs):
            constructor_args.append(kwargs)
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        def create(self, **kwargs):
            request_args.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(valid_payload())))])
        def close(self):
            closed.append(True)
    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeClient))
    feedback = ai_service.evaluate_writing(TEXT, TASK, use_ai=True, api_key="test-key")
    assert feedback["provider"] == "openai"
    assert constructor_args == [{"api_key": "test-key", "timeout": 20.0, "max_retries": 1}]
    assert request_args[0]["response_format"] == {"type": "json_object"}
    assert request_args[0]["messages"][0]["role"] == "system"
    assert all(name in request_args[0]["messages"][0]["content"] for name in SCORE_NAMES)
    assert json.loads(request_args[0]["messages"][1]["content"])["learner_response"] == TEXT
    assert closed == [True]
