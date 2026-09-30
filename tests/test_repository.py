import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from database.repository import Repository


def question(question_id="question-1"):
    return {"id": question_id, "skill": "Grammar", "topic": "present perfect",
            "prompt": "I ___ finished.", "answer": "have", "explanation": "Use have with I."}


def test_settings_and_attempts_survive_restart(tmp_path):
    path = tmp_path / "nested" / "learner.db"
    first = Repository(path)
    first.update_settings({"learner_name": "Anna", "daily_minutes": 45, "exam_date": "2027-02-03"})
    assert first.record_attempt(question(), "has", False, "submit-1")
    restarted = Repository(path)
    restarted.init_schema()
    assert restarted.get_settings()["learner_name"] == "Anna"
    assert restarted.get_settings()["daily_minutes"] == 45
    assert restarted.get_settings()["exam_date"] == "2027-02-03"
    assert restarted.get_attempts()[0]["correct"] is False
    assert restarted.get_mistakes()[0]["wrong_count"] == 1
    assert not restarted.record_attempt(question(), "has", False, "submit-1")
    assert len(restarted.get_attempts()) == 1


def test_duplicate_submission_does_not_change_mistake(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    repo.record_attempt(question(), "has", False, "first")
    # An accidental rerun with the same token cannot reverse the result.
    assert not repo.record_attempt(question(), "have", True, "first")
    assert repo.get_mistakes()[0]["resolved"] is False
    repo.record_attempt(question(), "has", False, "second")
    assert repo.get_mistakes()[0]["wrong_count"] == 2
    assert repo.record_attempt(question(), "have", True, "retry")
    assert repo.get_mistakes() == []
    assert repo.get_mistakes(include_resolved=True)[0]["resolved"] is True
    repo.record_attempt(question(), "has", False, "after-retry")
    assert repo.get_mistakes()[0]["wrong_count"] == 3
    repo.resolve_mistake("question-1")
    assert repo.get_mistakes() == []


def test_same_token_from_two_tabs_is_recorded_once(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    with ThreadPoolExecutor(max_workers=2) as pool:
        inserted = list(pool.map(lambda _: repo.record_attempt(question(), "has", False, "shared-token"), range(2)))
    assert sorted(inserted) == [False, True]
    assert len(repo.get_attempts()) == 1
    assert repo.get_mistakes()[0]["wrong_count"] == 1


@pytest.mark.parametrize("changes", [
    {"daily_minutes": 4}, {"daily_minutes": 241}, {"daily_minutes": True},
    {"daily_minutes": 20.0}, {"ai_enabled": "true"}, {"exam_date": "2027-02-30"},
    {"exam_date": "20270203"}, {"learner_name": " "}, {"openai_model": ""},
    {"api_key": "must-not-store"}, {"OPENAI_API_KEY": "must-not-store"},
])
def test_invalid_settings_are_rejected_atomically(tmp_path, changes):
    repo = Repository(tmp_path / "learner.db")
    before = repo.get_settings()
    with pytest.raises(ValueError):
        repo.update_settings({"learner_name": "Not saved", **changes})
    assert repo.get_settings() == before


def test_settings_partial_update_and_default_path_environment(tmp_path, monkeypatch):
    path = tmp_path / "env.db"
    monkeypatch.setenv("B1_DB_PATH", str(path))
    repo = Repository()
    repo.update_settings({"ai_enabled": True})
    assert repo.path == str(path)
    assert repo.get_settings()["daily_minutes"] == 20
    assert repo.get_settings()["ai_enabled"] is True
    repo.update_settings({"exam_date": ""})
    assert repo.get_settings()["exam_date"] == ""


def test_in_memory_repository_keeps_data_between_operations():
    repo = Repository(":memory:")
    repo.record_attempt(question(), "have", True)
    assert len(repo.get_attempts()) == 1


@pytest.mark.parametrize("kwargs", [
    {"user_answer": None, "correct": False}, {"user_answer": "has", "correct": 1},
    {"user_answer": "has", "correct": False, "attempt_id": ""},
])
def test_attempt_validation_prevents_partial_writes(tmp_path, kwargs):
    repo = Repository(tmp_path / "learner.db")
    with pytest.raises(ValueError):
        repo.record_attempt(question(), **kwargs)
    assert repo.get_attempts() == []
    assert repo.get_mistakes() == []


def test_writing_feedback_json_and_idempotency_persist(tmp_path):
    path = tmp_path / "learner.db"
    repo = Repository(path)
    feedback = {"provider": "offline", "scores": {"Content": 3}, "strengths": ["Good greeting"]}
    assert repo.save_writing("email-1", "Email", "Dear Sam, ...", feedback, "submission-1")
    assert not repo.save_writing("email-1", "Email", "Dear Sam, ...", feedback, "submission-1")
    stored = Repository(path).get_writing()
    assert len(stored) == 1
    assert stored[0]["feedback"] == feedback
    exported = repo.export_data()
    assert set(exported) == {"settings", "attempts", "mistakes", "vocabulary", "writing"}
    assert "api_key" not in json.dumps(exported).lower()
    with pytest.raises(ValueError):
        repo.save_writing("email-1", "Email", "Dear Sam", {"bad": float("nan")})
    with pytest.raises(ValueError):
        repo.save_writing("email-1", "Essay", "Dear Sam", {})
    with pytest.raises(ValueError):
        repo.save_writing("email-1", {}, "Dear Sam", {})
    assert len(repo.get_writing()) == 1


def test_user_text_is_parameterized_and_preserved(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    text = "I'm learning'); DROP TABLE attempts; --"
    repo.record_attempt(question(), text, False)
    repo.save_writing("story", "Story", text, {"improvements": [text]})
    assert repo.get_attempts()[0]["user_answer"] == text
    assert repo.get_writing()[0]["text"] == text
    assert repo.get_writing()[0]["feedback"]["improvements"] == [text]
