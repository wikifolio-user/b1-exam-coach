from concurrent.futures import ThreadPoolExecutor

import pytest

from database.repository import Repository


CARDS = [
    {"id": "journey", "word": "journey", "meaning": "Reise", "example": "The journey took two hours.", "topic": "travel"},
    {"id": "borrow", "word": "borrow", "meaning": "ausleihen", "example": "Can I borrow your book?", "topic": "daily life"},
]


def test_unseen_cards_due_and_good_review_intervals_survive_restart(tmp_path):
    path = tmp_path / "learner.db"
    repo = Repository(path)
    assert len(repo.due_cards(CARDS, "2026-09-30")) == 2
    first = repo.review_card("journey", 2, "2026-09-30", "review-1")
    assert first == {"card_id": "journey", "repetitions": 1, "interval_days": 1, "ease": 2.5, "due_date": "2026-10-01"}
    assert [card["id"] for card in repo.due_cards(CARDS, "2026-09-30")] == ["borrow"]
    restarted = Repository(path)
    assert len(restarted.due_cards(CARDS, "2026-10-01")) == 2
    second = restarted.review_card("journey", 2, "2026-10-01", "review-2")
    assert second["interval_days"] == 3
    assert second["due_date"] == "2026-10-04"
    third = restarted.review_card("journey", 2, "2026-10-04", "review-3")
    assert third["interval_days"] == 8
    assert third["due_date"] == "2026-10-12"
    assert restarted.get_vocab_states()[0] == third
    assert len(restarted.get_attempts()) == 3
    assert all(attempt["skill"] == "Vocabulary" and attempt["topic"] == "travel" for attempt in restarted.get_attempts())


def test_again_resets_repetitions_and_records_then_resolves_mistake(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    repo.due_cards(CARDS, "2026-09-30")
    easy = repo.review_card("journey", 3, "2026-09-30", "easy")
    assert easy["interval_days"] == 4
    again = repo.review_card("journey", 0, "2026-10-04", "again")
    assert again["repetitions"] == 0
    assert again["interval_days"] == 1
    assert again["due_date"] == "2026-10-05"
    assert again["ease"] < easy["ease"]
    mistake = repo.get_mistakes()[0]
    assert (mistake["question_id"], mistake["topic"], mistake["answer"]) == ("journey", "travel", "Reise")
    repo.review_card("journey", 2, "2026-10-05", "recalled")
    assert repo.get_mistakes() == []


def test_review_idempotency_and_concurrent_tabs(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    repo.due_cards(CARDS, "2026-09-30")
    with ThreadPoolExecutor(max_workers=2) as pool:
        states = list(pool.map(lambda _: repo.review_card("journey", 2, "2026-09-30", "shared-review"), range(2)))
    assert states[0] == states[1]
    assert len(repo.get_attempts()) == 1
    repo.review_card("journey", 2, "2026-10-01", "second-review")
    # Replaying an old action returns that action's saved result, without changing today's state.
    assert repo.review_card("journey", 0, "2026-10-04", "shared-review") == states[0]
    assert repo.get_vocab_states()[0]["repetitions"] == 2
    assert len(repo.get_attempts()) == 2
    with pytest.raises(ValueError):
        repo.review_card("borrow", 2, "2026-10-04", "shared-review")


@pytest.mark.parametrize("quality", [-1, 4, 2.0, True, "Good"])
def test_invalid_quality_does_not_record_review(tmp_path, quality):
    repo = Repository(tmp_path / "learner.db")
    repo.due_cards(CARDS, "2026-09-30")
    with pytest.raises(ValueError):
        repo.review_card("journey", quality, "2026-09-30")
    assert repo.get_vocab_states() == []
    assert repo.get_attempts() == []


def test_bad_dates_unknown_cards_and_duplicate_card_ids_are_rejected(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    with pytest.raises(ValueError):
        repo.review_card("unknown", 2, "2026-09-30")
    with pytest.raises(ValueError):
        repo.due_cards(CARDS, "2026-02-30")
    with pytest.raises(ValueError):
        repo.due_cards(CARDS, "20260930")
    with pytest.raises(ValueError):
        repo.due_cards([CARDS[0], CARDS[0]], "2026-09-30")
    with pytest.raises(ValueError):
        repo.review_card("journey", 2, "2026-09-30")


def test_hard_reviews_never_reduce_ease_below_floor(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    repo.due_cards(CARDS, "2026-09-30")
    for index in range(20):
        state = repo.review_card("borrow", 1, "2026-09-30", f"hard-{index}")
    assert state["ease"] == 1.3
    assert state["interval_days"] == 1
    assert repo.get_mistakes()[0]["wrong_count"] == 20


def test_successful_reviews_remain_due_within_a_year(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    repo.due_cards(CARDS, "2026-09-30")
    for index in range(30):
        state = repo.review_card("journey", 3, "2026-09-30", f"easy-{index}")
    assert state["interval_days"] == 365
    assert state["due_date"] == "2027-09-30"
    assert state["ease"] <= 3.5


def test_leap_day_scheduling_and_unrepresentable_dates(tmp_path):
    repo = Repository(tmp_path / "learner.db")
    repo.due_cards(CARDS, "2028-02-28")
    assert repo.review_card("journey", 2, "2028-02-28")["due_date"] == "2028-02-29"
    before = repo.get_vocab_states()
    with pytest.raises(ValueError, match="too late"):
        repo.review_card("borrow", 2, "9999-12-31")
    assert repo.get_vocab_states() == before
    assert len(repo.get_attempts()) == 1
