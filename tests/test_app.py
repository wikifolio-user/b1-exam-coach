"""User-facing Streamlit flows against a fresh, local SQLite database.

The navigation uses callable pages, which AppTest cannot switch to by filename.
We smoke-test the real entry point and exercise the same render functions through
small page harnesses. No AI request or external service is needed.
"""

from datetime import date, timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from components.common import _repository
from data.content import load_grammar, load_reading, load_vocabulary, load_writing
from database.repository import Repository
from services import ai_service
from services.writing_service import evaluate_offline


APP_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def learner(tmp_path, monkeypatch):
    """Keep UI tests away from both the developer database and the network."""
    path = tmp_path / "ui-learner.db"
    monkeypatch.setenv("B1_DB_PATH", str(path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def forbidden_request(*args, **kwargs):
        pytest.fail("An offline UI test attempted an external AI request.")

    monkeypatch.setattr(ai_service, "_request_feedback", forbidden_request)
    _repository.clear()
    yield Repository(path)
    _repository.clear()


def page(name):
    app = AppTest.from_string(
        f"from pages import {name}\n{name}.render()", default_timeout=10
    ).run()
    assert not app.exception, [item.message for item in app.exception]
    return app


def button(app, label):
    return next(item for item in app.button if item.label == label)


def metric(app, label):
    return next(item.value for item in app.metric if item.label == label)


def answer_quiz(app, questions, *, wrong_first=False):
    """Set actual UI widgets; the form submit is a separate user action."""
    radios = iter(app.radio)
    inputs = iter(app.text_input)
    for index, question in enumerate(questions):
        answer = question["answer"]
        if wrong_first and index == 0:
            answer = next(
                (option for option in question["options"] if option != answer),
                "incorrect-word",
            )
        if question["options"]:
            next(radios).set_value(answer)
        else:
            next(inputs).set_value(answer)
    button(app, "Check answers").click().run()
    assert not app.exception


def test_real_root_launch_uses_isolated_database_and_dashboard(learner):
    app = AppTest.from_file(str(APP_ROOT / "app.py"), default_timeout=10).run()
    assert not app.exception
    assert app.main.title[0].value == "Your next step towards B1"
    assert any("B1 Exam Coach" in title.value for title in app.sidebar.title)
    assert metric(app, "Practice answers") == "0"
    assert metric(app, "Words due") == str(len(load_vocabulary()))
    assert learner.get_attempts() == []


@pytest.mark.parametrize(
    ("name", "title"),
    [
        ("dashboard", "Your next step towards B1"),
        ("study_plan", "Study Plan"),
        ("reading", "Reading Trainer"),
        ("grammar", "Grammar Trainer"),
        ("vocabulary", "Vocabulary Trainer"),
        ("writing", "Writing Trainer"),
        ("mistakes", "My Mistakes"),
        ("progress", "Progress"),
        ("settings", "Settings"),
    ],
)
def test_every_page_renders_for_a_new_learner(learner, name, title):
    app = page(name)
    assert app.title[0].value == title
    assert learner.get_attempts() == []
    assert learner.get_writing() == []


@pytest.mark.parametrize("part", range(1, 7))
def test_all_reading_parts_validate_save_feedback_and_retry(learner, part):
    app = page("reading")
    app.selectbox[0].set_value(part).run()
    practice = next(item for item in load_reading() if item["part"] == part)
    questions = practice["questions"]
    assert app.subheader[0].value == practice["title"]
    assert len(app.radio) + len(app.text_input) == len(questions)
    assert not any(item.value.startswith("Answer: ") for item in app.markdown)

    button(app, "Check answers").click().run()
    assert not app.exception
    assert any("Answer every question" in item.value for item in app.warning)
    assert learner.get_attempts() == []

    answer_quiz(app, questions, wrong_first=True)
    attempts = learner.get_attempts()
    assert len(attempts) == len(questions)
    assert sum(item["correct"] for item in attempts) == len(questions) - 1
    assert {item["skill"] for item in attempts} == {"Reading"}
    assert learner.get_mistakes()[0]["question_id"] == questions[0]["id"]
    assert all(item.disabled for item in [*app.radio, *app.text_input])
    assert button(app, "Check answers").disabled
    assert any("Your progress has been saved" in item.value for item in app.success)
    assert any(questions[0]["explanation"] in item.value for item in app.markdown)

    # Unrelated Streamlit reruns must not save the submitted batch again.
    app.run()
    assert learner.get_attempts() == attempts
    button(app, "Try again").click().run()
    assert all(not item.disabled for item in [*app.radio, *app.text_input])
    answer_quiz(app, questions)
    assert len(learner.get_attempts()) == 2 * len(questions)
    assert learner.get_mistakes() == []
    assert learner.get_mistakes(include_resolved=True)[0]["resolved"] is True


def test_reading_second_set_is_available_in_each_part(learner):
    app = page("reading")
    for part in range(1, 7):
        app.selectbox[0].set_value(part).run()
        practices = [item for item in load_reading() if item["part"] == part]
        assert len(app.selectbox[1].options) == len(practices)
        app.selectbox[1].set_value(practices[-1]).run()
        assert not app.exception
        assert app.subheader[0].value == practices[-1]["title"]
    assert learner.get_attempts() == []


def test_grammar_saves_answer_and_next_question_changes_prompt(learner):
    app = page("grammar")
    current = app.session_state["grammar_current_Adaptive practice"]
    answer_quiz(app, [current])
    assert learner.get_attempts()[0]["question_id"] == current["id"]
    assert learner.get_attempts()[0]["correct"] is True
    app.run()
    assert len(learner.get_attempts()) == 1
    button(app, "Next question").click().run()
    assert not app.exception
    following = app.session_state["grammar_current_Adaptive practice"]
    assert following["id"] != current["id"]
    assert app.radio[0].value is None
    assert not button(app, "Check answers").disabled


def test_grammar_next_skips_an_unanswered_question_without_saving(learner):
    app = page("grammar")
    current = app.session_state["grammar_current_Adaptive practice"]
    button(app, "Next question").click().run()
    assert not app.exception
    assert app.session_state["grammar_current_Adaptive practice"]["id"] != current["id"]
    assert app.radio[0].value is None
    assert learner.get_attempts() == []


def test_grammar_topic_selection_and_adaptive_weakness(learner):
    questions = load_grammar()
    topic = questions[0]["topic"]
    for question in [item for item in questions if item["topic"] == topic]:
        learner.record_attempt(question, "incorrect", False)
    app = page("grammar")
    assert app.session_state["grammar_current_Adaptive practice"]["topic"] == topic
    another_topic = next(item["topic"] for item in questions if item["topic"] != topic)
    app.selectbox[0].set_value(another_topic).run()
    assert not app.exception
    assert app.session_state["grammar_current_" + another_topic]["topic"] == another_topic


def test_vocabulary_reveal_and_good_schedules_one_logged_review(learner):
    cards = load_vocabulary()
    expected_card = learner.due_cards(cards)[0]
    app = page("vocabulary")
    assert app.header[0].value == expected_card["word"]
    assert not any(item.value == expected_card["meaning"] for item in app.subheader)
    assert not any(item.label == "Good" for item in app.button)
    button(app, "Reveal meaning").click().run()
    assert app.subheader[0].value == expected_card["meaning"]
    button(app, "Good").click().run()
    assert not app.exception
    state = learner.get_vocab_states()[0]
    assert state["card_id"] == expected_card["id"]
    assert state["repetitions"] == 1
    assert state["due_date"] == (date.today() + timedelta(days=1)).isoformat()
    attempts = learner.get_attempts()
    assert len(attempts) == 1
    assert attempts[0]["skill"] == "Vocabulary"
    assert attempts[0]["user_answer"] == "Good"
    assert attempts[0]["correct"] is True
    assert app.header[0].value != expected_card["word"]
    assert metric(app, "Words practised") == "1"
    app.run()
    assert learner.get_attempts() == attempts


def test_vocabulary_again_adds_mistake_with_visible_meaning(learner):
    expected_card = learner.due_cards(load_vocabulary())[0]
    app = page("vocabulary")
    button(app, "Reveal meaning").click().run()
    button(app, "Again").click().run()
    assert not app.exception
    mistake = learner.get_mistakes()[0]
    assert mistake["question_id"] == expected_card["id"]
    assert mistake["skill"] == "Vocabulary"
    assert learner.get_vocab_states()[0]["repetitions"] == 0
    review = page("mistakes")
    assert any(
        item.value == f"Correct answer: {expected_card['meaning']}" for item in review.markdown
    )
    assert any(expected_card["example"] == item.value for item in review.markdown)
    assert any("when it is due" in item.value for item in review.caption)


@pytest.mark.parametrize("kind", ["Email", "Article", "Story"])
def test_offline_writing_rejects_empty_then_saves_draft_and_feedback(learner, kind):
    app = page("writing")
    app.selectbox[0].set_value(kind).run()
    task = next(item for item in load_writing() if item["kind"] == kind)
    assert app.checkbox[0].disabled
    assert app.checkbox[0].value is False
    button(app, "Get feedback and save").click().run()
    assert any("Write a draft" in item.value for item in app.warning)
    assert learner.get_writing() == []

    text = (
        "Hi Sam,\n\nThank you for your message. I would love to come on Saturday. "
        "We can meet at the station and travel together. I enjoy learning new things "
        "because it helps me understand the world. Last weekend I visited the park "
        "with my friends. First we played a game, then we had lunch. Although it "
        "was raining, everyone had a wonderful time. I will bring some sandwiches "
        "and a warm coat. Please let me know what time we should meet. "
        "I hope to see you soon.\n\nBest wishes,\nAlex"
    )
    if task["starter"]:
        text = task["starter"] + "\n\n" + text
    app.text_area[0].set_value(text)
    button(app, "Get feedback and save").click().run()
    assert not app.exception
    drafts = learner.get_writing()
    assert len(drafts) == 1
    assert drafts[0]["kind"] == kind
    assert drafts[0]["task_id"] == task["id"]
    assert drafts[0]["text"] == text
    assert drafts[0]["feedback"]["provider"] == "offline"
    assert len(drafts[0]["feedback"]["scores"]) == 4
    assert any("Feedback provider: offline" in item.value for item in app.caption)
    assert any("cannot verify meaning" in item.value for item in app.warning)
    app.run()
    assert learner.get_writing() == drafts
    restarted = page("writing")
    restarted.selectbox[0].set_value(kind).run()
    assert any("Saved drafts for this task (1)" == item.label for item in restarted.expander)


@pytest.mark.parametrize("changed", ["setting", "key"])
def test_stale_ai_checkbox_cannot_bypass_current_configuration(learner, monkeypatch, changed):
    from pages import writing

    learner.update_settings({"ai_enabled": True})
    monkeypatch.setattr(writing, "api_key", lambda: "ui-test-key")
    calls = []

    def capture_evaluation(text, task, **kwargs):
        calls.append(kwargs)
        return evaluate_offline(text, task)

    monkeypatch.setattr(writing, "evaluate_writing", capture_evaluation)
    app = page("writing")
    assert not app.checkbox[0].disabled
    app.checkbox[0].set_value(True).run()
    if changed == "setting":
        learner.update_settings({"ai_enabled": False})
    else:
        monkeypatch.setattr(writing, "api_key", lambda: None)
    app.run()
    assert app.checkbox[0].disabled
    # Streamlit keeps the prior form choice when configuration changes.
    assert app.checkbox[0].value is True
    app.text_area[0].set_value("Dear Sam, thank you for your email. See you on Saturday.")
    button(app, "Get feedback and save").click().run()
    assert not app.exception
    assert len(calls) == 1
    assert calls[0]["use_ai"] is False
    assert learner.get_writing()[0]["feedback"]["provider"] == "offline"


def test_settings_persist_profile_goal_and_exam_date(learner):
    app = page("settings")
    app.text_input[0].set_value("Lena")
    app.number_input[0].set_value(45)
    app.checkbox[0].set_value(True)
    app.date_input[0].set_value(date(2027, 3, 15))
    button(app, "Save settings").click().run()
    assert not app.exception
    settings = Repository(learner.path).get_settings()
    assert settings["learner_name"] == "Lena"
    assert settings["daily_minutes"] == 45
    assert settings["exam_date"] == "2027-03-15"
    assert settings["ai_enabled"] is False
    restarted = page("settings")
    assert restarted.text_input[0].value == "Lena"
    assert restarted.number_input[0].value == 45
    assert restarted.date_input[0].value == date(2027, 3, 15)
    dashboard = page("dashboard")
    assert any("Welcome, Lena" in item.value for item in dashboard.caption)
    plan = page("study_plan")
    assert any("45-minute plan" in item.value for item in plan.caption)
    assert "api_key" not in settings


def test_settings_empty_name_reports_validation_without_partial_save(learner):
    before = learner.get_settings()
    app = page("settings")
    app.text_input[0].set_value("   ")
    app.number_input[0].set_value(35)
    button(app, "Save settings").click().run()
    assert not app.exception
    assert app.error
    assert learner.get_settings() == before


def test_mistake_retry_resolves_and_progress_displays_saved_learning(learner):
    question = load_grammar()[0]
    learner.record_attempt(question, "incorrect", False)
    app = page("mistakes")
    assert app.radio[0].label.endswith(question["prompt"])
    answer_quiz(app, [question])
    assert learner.get_mistakes() == []
    resolved = learner.get_mistakes(include_resolved=True)
    assert resolved[0]["resolved"] is True
    assert any("No mistakes to review" in item.value for item in app.info)
    app.checkbox[0].set_value(True).run()
    assert not app.exception
    assert any("✅ Grammar" in item.value for item in app.markdown)

    task = load_writing()[0]
    draft = "Dear Sam, thank you for your invitation. I can come on Saturday. Best wishes, Alex"
    learner.save_writing(task["id"], task["kind"], draft, evaluate_offline(draft, task))
    progress = page("progress")
    assert metric(progress, "Answers") == "2"
    assert metric(progress, "Accuracy") == "50%"
    assert metric(progress, "Writing drafts") == "1"
    assert {item.value for item in progress.subheader} >= {
        "Answers per study day",
        "Topic performance",
        "Writing estimates over time",
    }
    assert len(progress.dataframe) == 2
    dashboard = page("dashboard")
    assert metric(dashboard, "Practice answers") == "2"
    assert metric(dashboard, "Accuracy") == "50%"
    plan = page("study_plan")
    assert not plan.exception
    assert len(plan.subheader) >= 4
