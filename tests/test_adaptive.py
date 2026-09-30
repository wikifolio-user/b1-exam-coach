import pytest

from services.adaptive_service import build_study_plan, choose_question, topic_stats


def attempt(question_id, topic, correct, skill="Grammar"):
    return {"question_id": question_id, "skill": skill, "topic": topic, "correct": correct}


def test_bayesian_mastery_reflects_evidence_and_weak_topics():
    attempts = [attempt("q-weak", "past tense", False)] * 4 + [attempt("q-strong", "articles", True)] * 4
    stats = {row["topic"]: row for row in topic_stats(attempts)}
    assert stats["past tense"]["accuracy"] == 0
    assert stats["articles"]["accuracy"] == 1
    assert stats["past tense"]["mastery"] == pytest.approx(1 / 6)
    assert stats["past tense"]["weakness"] > stats["articles"]["weakness"]
    assert topic_stats([attempt("q", "articles", True)])[0]["mastery"] < 0.75
    assert topic_stats([]) == []


def test_question_selection_targets_weak_topics_and_less_recent_items():
    questions = [
        {"id": "q-strong", "skill": "Grammar", "topic": "articles"},
        {"id": "q-old", "skill": "Grammar", "topic": "past tense"},
        {"id": "q-recent", "skill": "Grammar", "topic": "past tense"},
    ]
    attempts = [attempt("q-old", "past tense", False), attempt("q-strong", "articles", True),
                attempt("q-strong", "articles", True), attempt("q-recent", "past tense", False)]
    assert choose_question(questions, attempts)["id"] == "q-old"
    assert choose_question(questions, attempts, topic="articles")["id"] == "q-strong"
    assert choose_question(questions, attempts, topic="unknown") is None
    assert choose_question([], attempts) is None


def test_unseen_items_can_be_reached_within_topic():
    questions = [{"id": "seen", "skill": "Grammar", "topic": "articles"},
                 {"id": "unseen", "skill": "Grammar", "topic": "articles"}]
    assert choose_question(questions, [attempt("seen", "articles", True)])["id"] == "unseen"


@pytest.mark.parametrize("minutes", [5, 7, 20, 45, 120, 240])
def test_daily_plan_allocates_exact_budget_with_every_skill_reachable(minutes):
    plan = build_study_plan([], {"daily_minutes": minutes}, due_count=5)
    assert sum(item["minutes"] for item in plan) == minutes
    assert {item["skill"] for item in plan} == {"Reading", "Grammar", "Vocabulary", "Writing"}
    assert all(type(item["minutes"]) is int and item["minutes"] > 0 for item in plan)
    assert all(item["topic"] == "initial practice" for item in plan)
    assert "initial feedback" in next(item["reason"] for item in plan if item["skill"] == "Writing")


def test_plan_targets_weakest_topic_and_due_backlog():
    attempts = [attempt("weak", "past tense", False)] * 8 + [attempt("strong", "articles", True)] * 8
    without_due = {item["skill"]: item for item in build_study_plan(attempts, {"daily_minutes": 40}, 0, 4)}
    with_due = {item["skill"]: item for item in build_study_plan(attempts, {"daily_minutes": 40}, 30, 4)}
    assert without_due["Grammar"]["topic"] == "past tense"
    assert "0/8" in without_due["Grammar"]["reason"]
    assert with_due["Vocabulary"]["minutes"] > without_due["Vocabulary"]["minutes"]
    assert "30 cards" in with_due["Vocabulary"]["reason"]
    assert "saved writing" in with_due["Writing"]["reason"]


@pytest.mark.parametrize("kwargs", [
    {"settings": {"daily_minutes": True}, "due_count": 0},
    {"settings": {"daily_minutes": 0}, "due_count": 0},
    {"settings": {"daily_minutes": 20}, "due_count": -1},
    {"settings": {"daily_minutes": 20}, "due_count": 0, "writing_count": 1.5},
])
def test_plan_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        build_study_plan([], **kwargs)


def test_invalid_attempts_cannot_silently_distort_mastery():
    with pytest.raises(ValueError):
        topic_stats([attempt("q", "articles", "false")])
