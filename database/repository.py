"""Transactional persistence for one local learner, without storing credentials.

Connections are short lived and writes are atomic. Optional action tokens make
Streamlit reruns safe: replaying a submitted answer does not count it twice.
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator


DEFAULT_SETTINGS = {
    "learner_name": "Learner",
    "daily_minutes": 20,
    "exam_date": "",
    "ai_enabled": False,
    "openai_model": "gpt-4.1-mini",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: Any, name: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f"{name} must be {'a' if empty else 'a non-empty'} string.")
    return value


def _token(value: Any, name: str) -> str | None:
    if value is None:
        return None
    result = _text(value, name)
    if len(result) > 200:
        raise ValueError(f"{name} must be at most 200 characters.")
    return result


def _day(value: Any = None) -> date:
    if value is None:
        return datetime.now(timezone.utc).date()
    if not isinstance(value, str):
        raise ValueError("Date must be an ISO date string (YYYY-MM-DD).")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Date must be an ISO date string (YYYY-MM-DD).") from error
    if parsed.isoformat() != value:
        raise ValueError("Date must be an ISO date string (YYYY-MM-DD).")
    return parsed


class Repository:
    """The SQLite data store. ``path`` may also be ``:memory:`` for tests."""

    def __init__(self, path: str | Path | None = None):
        selected = path if path is not None else os.getenv("B1_DB_PATH")
        selected = selected or Path(__file__).resolve().parents[1] / "b1_exam_coach.db"
        self.path = str(selected)
        self._anchor: sqlite3.Connection | None = None
        self._uri = self.path == ":memory:"
        if self._uri:
            self._dsn = f"file:b1-coach-{uuid.uuid4().hex}?mode=memory&cache=shared"
            self._anchor = sqlite3.connect(self._dsn, uri=True)
        else:
            db_path = Path(self.path).expanduser()
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.path = str(db_path)
            self._dsn = self.path
        self.init_schema()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._dsn, timeout=10, uri=self._uri)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def init_schema(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY, value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attempt_token TEXT UNIQUE,
                    question_id TEXT NOT NULL,
                    skill TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    user_answer TEXT NOT NULL,
                    correct INTEGER NOT NULL CHECK(correct IN (0, 1)),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS mistakes (
                    question_id TEXT PRIMARY KEY,
                    skill TEXT NOT NULL, topic TEXT NOT NULL,
                    prompt TEXT NOT NULL, answer TEXT NOT NULL,
                    user_answer TEXT NOT NULL, explanation TEXT NOT NULL,
                    wrong_count INTEGER NOT NULL CHECK(wrong_count > 0),
                    resolved INTEGER NOT NULL CHECK(resolved IN (0, 1)),
                    last_seen TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS vocabulary_cards (
                    card_id TEXT PRIMARY KEY,
                    word TEXT NOT NULL, meaning TEXT NOT NULL,
                    example TEXT NOT NULL, topic TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS vocabulary_states (
                    card_id TEXT PRIMARY KEY REFERENCES vocabulary_cards(card_id),
                    repetitions INTEGER NOT NULL CHECK(repetitions >= 0),
                    interval_days INTEGER NOT NULL CHECK(interval_days >= 1),
                    ease REAL NOT NULL CHECK(ease >= 1.3),
                    due_date TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS vocabulary_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    review_token TEXT UNIQUE,
                    card_id TEXT NOT NULL REFERENCES vocabulary_cards(card_id),
                    quality INTEGER NOT NULL CHECK(quality BETWEEN 0 AND 3),
                    review_date TEXT NOT NULL,
                    state TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS writing_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_token TEXT UNIQUE,
                    task_id TEXT NOT NULL, kind TEXT NOT NULL,
                    text TEXT NOT NULL, feedback TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS attempts_skill_topic ON attempts(skill, topic);
                CREATE INDEX IF NOT EXISTS vocabulary_due_date ON vocabulary_states(due_date);
                """
            )
            for key, value in DEFAULT_SETTINGS.items():
                connection.execute(
                    "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
                    (key, json.dumps(value)),
                )

    def get_settings(self) -> dict:
        with self._connection() as connection:
            rows = connection.execute("SELECT key, value FROM settings").fetchall()
        result = DEFAULT_SETTINGS.copy()
        result.update({row["key"]: json.loads(row["value"]) for row in rows if row["key"] in DEFAULT_SETTINGS})
        return result

    def update_settings(self, values: dict) -> None:
        if not isinstance(values, dict):
            raise ValueError("Settings must be a dictionary.")
        unknown = set(values) - set(DEFAULT_SETTINGS)
        if unknown:
            raise ValueError("Only learner_name, daily_minutes, exam_date, ai_enabled and openai_model may be stored.")
        validated = {}
        for key, value in values.items():
            if key == "daily_minutes":
                if type(value) is not int or not 5 <= value <= 240:
                    raise ValueError("daily_minutes must be an integer between 5 and 240.")
            elif key == "ai_enabled":
                if type(value) is not bool:
                    raise ValueError("ai_enabled must be a boolean.")
            elif key == "exam_date":
                _text(value, key, empty=True)
                if value:
                    _day(value)
            else:
                value = _text(value, key).strip()
                if len(value) > 100:
                    raise ValueError(f"{key} must be at most 100 characters.")
            validated[key] = value
        with self._connection() as connection:
            for key, value in validated.items():
                connection.execute(
                    "INSERT INTO settings(key, value) VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, json.dumps(value)),
                )

    @staticmethod
    def _question(question: dict) -> dict:
        if not isinstance(question, dict):
            raise ValueError("Question must be a dictionary.")
        return {
            key: _text(question.get(key), f"question.{key}", empty=key in {"prompt", "answer", "explanation"})
            for key in ("id", "skill", "topic", "prompt", "answer", "explanation")
        }

    @staticmethod
    def _insert_attempt(connection, question: dict, user_answer: str, correct: bool, token: str | None) -> bool:
        now = _now()
        cursor = connection.execute(
            "INSERT OR IGNORE INTO attempts(attempt_token, question_id, skill, topic, user_answer, correct, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (token, question["id"], question["skill"], question["topic"], user_answer, int(correct), now),
        )
        if cursor.rowcount == 0:
            return False
        if correct:
            connection.execute("UPDATE mistakes SET resolved=1, last_seen=? WHERE question_id=?", (now, question["id"]))
        else:
            connection.execute(
                "INSERT INTO mistakes(question_id, skill, topic, prompt, answer, user_answer, explanation, wrong_count, resolved, last_seen) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, ?) "
                "ON CONFLICT(question_id) DO UPDATE SET skill=excluded.skill, topic=excluded.topic, "
                "prompt=excluded.prompt, answer=excluded.answer, user_answer=excluded.user_answer, "
                "explanation=excluded.explanation, wrong_count=mistakes.wrong_count+1, resolved=0, last_seen=excluded.last_seen",
                (question["id"], question["skill"], question["topic"], question["prompt"], question["answer"],
                 user_answer, question["explanation"], now),
            )
        return True

    def record_attempt(self, question: dict, user_answer: str, correct: bool, attempt_id: str | None = None) -> bool:
        question = self._question(question)
        _text(user_answer, "user_answer", empty=True)
        if type(correct) is not bool:
            raise ValueError("correct must be a boolean.")
        token = _token(attempt_id, "attempt_id")
        with self._connection() as connection:
            return self._insert_attempt(connection, question, user_answer, correct, token)

    def get_attempts(self) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, question_id, skill, topic, user_answer, correct, created_at FROM attempts ORDER BY id"
            ).fetchall()
        return [dict(row) | {"correct": bool(row["correct"])} for row in rows]

    def get_mistakes(self, include_resolved: bool = False) -> list[dict]:
        if type(include_resolved) is not bool:
            raise ValueError("include_resolved must be a boolean.")
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM mistakes " + ("" if include_resolved else "WHERE resolved=0 ") + "ORDER BY last_seen DESC, question_id"
            ).fetchall()
        return [dict(row) | {"resolved": bool(row["resolved"])} for row in rows]

    def resolve_mistake(self, question_id: str) -> None:
        _text(question_id, "question_id")
        with self._connection() as connection:
            connection.execute("UPDATE mistakes SET resolved=1 WHERE question_id=?", (question_id,))

    def due_cards(self, cards: list[dict], today: str | None = None) -> list[dict]:
        day = _day(today).isoformat()
        if not isinstance(cards, list):
            raise ValueError("Cards must be a list.")
        validated = []
        ids = set()
        for card in cards:
            if not isinstance(card, dict):
                raise ValueError("Each card must be a dictionary.")
            clean = {
                key: _text(card.get(key), f"card.{key}", empty=key == "example")
                for key in ("id", "word", "meaning", "example", "topic")
            }
            if clean["id"] in ids:
                raise ValueError("Card IDs must be unique.")
            ids.add(clean["id"])
            validated.append((card, clean))
        with self._connection() as connection:
            for _, card in validated:
                connection.execute(
                    "INSERT INTO vocabulary_cards(card_id, word, meaning, example, topic) VALUES (?, ?, ?, ?, ?) "
                    "ON CONFLICT(card_id) DO UPDATE SET word=excluded.word, meaning=excluded.meaning, "
                    "example=excluded.example, topic=excluded.topic",
                    (card["id"], card["word"], card["meaning"], card["example"], card["topic"]),
                )
            states = {row["card_id"]: dict(row) for row in connection.execute("SELECT * FROM vocabulary_states")}
        due = []
        for original, card in validated:
            state = states.get(card["id"], {"card_id": card["id"], "repetitions": 0, "interval_days": 0, "ease": 2.5, "due_date": day})
            if state["due_date"] <= day:
                due.append(dict(original) | state)
        return sorted(due, key=lambda card: (card["due_date"], card["repetitions"], card["id"]))

    def review_card(self, card_id: str, quality: int, today: str | None = None, review_id: str | None = None) -> dict:
        _text(card_id, "card_id")
        if type(quality) is not int or not 0 <= quality <= 3:
            raise ValueError("quality must be an integer from 0 (Again) to 3 (Easy).")
        day = _day(today)
        token = _token(review_id, "review_id")
        with self._connection() as connection:
            # Acquire the write lock before reading state; two tabs cannot lose a review.
            connection.execute("BEGIN IMMEDIATE")
            if token is not None:
                previous = connection.execute("SELECT card_id, state FROM vocabulary_reviews WHERE review_token=?", (token,)).fetchone()
                if previous:
                    if previous["card_id"] != card_id:
                        raise ValueError("A review_id cannot be reused for another card.")
                    return json.loads(previous["state"])
            card = connection.execute("SELECT * FROM vocabulary_cards WHERE card_id=?", (card_id,)).fetchone()
            if card is None:
                raise ValueError("Unknown vocabulary card; call due_cards with your cards before reviewing.")
            row = connection.execute("SELECT * FROM vocabulary_states WHERE card_id=?", (card_id,)).fetchone()
            old = dict(row) if row else {"repetitions": 0, "interval_days": 0, "ease": 2.5}
            repetitions, interval, ease = old["repetitions"], old["interval_days"], old["ease"]
            if quality == 0:
                repetitions, interval, ease = 0, 1, max(1.3, ease - 0.2)
            elif quality == 1:
                repetitions += 1
                interval, ease = max(1, math.floor(interval * 1.2 + 0.5)), max(1.3, ease - 0.15)
            elif quality == 2:
                interval = 1 if repetitions == 0 else 3 if repetitions == 1 else max(interval + 1, math.floor(interval * ease + 0.5))
                repetitions += 1
            else:
                interval = 4 if repetitions == 0 else max(interval + 1, math.floor(interval * ease * 1.3 + 0.5))
                repetitions, ease = repetitions + 1, min(3.5, ease + 0.15)
            # Even well-known words get an annual refresher. Without a cap,
            # repeated successful reviews could schedule a word centuries away.
            interval = min(interval, 365)
            try:
                due_date = (day + timedelta(days=interval)).isoformat()
            except OverflowError as error:
                raise ValueError("The review date is too late to schedule its next repetition.") from error
            state = {"card_id": card_id, "repetitions": repetitions, "interval_days": interval,
                     "ease": round(ease, 3), "due_date": due_date}
            connection.execute(
                "INSERT INTO vocabulary_states(card_id, repetitions, interval_days, ease, due_date) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(card_id) DO UPDATE SET repetitions=excluded.repetitions, interval_days=excluded.interval_days, ease=excluded.ease, due_date=excluded.due_date",
                tuple(state[key] for key in ("card_id", "repetitions", "interval_days", "ease", "due_date")),
            )
            connection.execute(
                "INSERT INTO vocabulary_reviews(review_token, card_id, quality, review_date, state) VALUES (?, ?, ?, ?, ?)",
                (token, card_id, quality, day.isoformat(), json.dumps(state)),
            )
            question = {"id": card_id, "skill": "Vocabulary", "topic": card["topic"], "prompt": card["word"],
                        "answer": card["meaning"], "explanation": card["example"]}
            self._insert_attempt(connection, question, ("Again", "Hard", "Good", "Easy")[quality], quality >= 2, None)
            return state

    def get_vocab_states(self) -> list[dict]:
        with self._connection() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM vocabulary_states ORDER BY due_date, card_id")]

    def save_writing(self, task_id: str, kind: str, text: str, feedback: dict, submission_id: str | None = None) -> bool:
        _text(task_id, "task_id")
        if not isinstance(kind, str) or kind not in {"Email", "Article", "Story"}:
            raise ValueError("kind must be Email, Article or Story.")
        _text(text, "text")
        if not isinstance(feedback, dict):
            raise ValueError("feedback must be a dictionary.")
        try:
            encoded = json.dumps(feedback, allow_nan=False)
        except (TypeError, ValueError) as error:
            raise ValueError("feedback must contain JSON-compatible values.") from error
        token = _token(submission_id, "submission_id")
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO writing_submissions(submission_token, task_id, kind, text, feedback, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (token, task_id, kind, text, encoded, _now()),
            )
            return cursor.rowcount == 1

    def get_writing(self) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute("SELECT id, task_id, kind, text, feedback, created_at FROM writing_submissions ORDER BY id").fetchall()
        return [dict(row) | {"feedback": json.loads(row["feedback"])} for row in rows]

    def export_data(self) -> dict:
        return {"settings": self.get_settings(), "attempts": self.get_attempts(),
                "mistakes": self.get_mistakes(include_resolved=True), "vocabulary": self.get_vocab_states(),
                "writing": self.get_writing()}
