from datetime import date

import pytest

from services.progress_service import learning_summary
from services.scoring_service import answer_matches


@pytest.mark.parametrize("answer", ["That", " THAT ", "which"])
def test_accepted_open_cloze_answers(answer):
    assert answer_matches(answer, {"answer": "that", "accepted_answers": ["which"]})


def test_wrong_and_extra_word_answers_are_rejected():
    question = {"answer": "at"}
    assert not answer_matches("in", question)
    assert not answer_matches("at home", question)
    assert not answer_matches("", question)


def test_summary_counts_writing_and_streak_without_inventing_accuracy():
    empty = learning_summary([], [], date(2026, 9, 30))
    assert empty["accuracy"] is None
    assert empty["streak"] == 0
    writing = [{"created_at": "2026-09-29T10:00:00+00:00"}]
    result = learning_summary([], writing, date(2026, 9, 30))
    assert result["streak"] == 1
    assert result["today_count"] == 0
    assert result["writing_count"] == 1


def test_summary_streak_gaps_and_multiple_same_day_activities():
    attempts = [
        {"correct": True, "created_at": "2026-09-30T12:00:00+00:00"},
        {"correct": False, "created_at": "2026-09-30T13:00:00+00:00"},
        {"correct": True, "created_at": "2026-09-28T12:00:00+00:00"},
    ]
    writing = [{"created_at": "2026-09-29T11:00:00+00:00"}]
    result = learning_summary(attempts, writing, date(2026, 9, 30))
    assert result["streak"] == 3
    assert result["today_count"] == 2
    assert result["accuracy"] == pytest.approx(2 / 3)
    assert learning_summary(attempts, [], date(2026, 9, 30))["streak"] == 1
