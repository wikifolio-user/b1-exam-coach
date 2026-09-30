import os
from pathlib import Path
from uuid import uuid4

import streamlit as st

from database.repository import Repository
from services.scoring_service import answer_matches


@st.cache_resource
def _repository(path: str) -> Repository:
    return Repository(path)


def get_repository() -> Repository:
    path = os.getenv("B1_DB_PATH", str(Path(__file__).resolve().parents[1] / "b1_exam_coach.db"))
    return _repository(path)


def heading(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def quiz(questions: list[dict], key: str, repository: Repository) -> None:
    """One submission per round; explicit retry starts a new attempt."""
    result_key, token_key = key + "_results", key + "_token"
    if token_key not in st.session_state:
        st.session_state[token_key] = uuid4().hex
    submitted = result_key in st.session_state
    with st.form(key + "_form"):
        answers = {}
        for number, question in enumerate(questions, 1):
            label = f"{number}. {question['prompt']}"
            widget_key = f"{key}_{st.session_state[token_key]}_{question['id']}"
            if question["options"]:
                answers[question["id"]] = st.radio(
                    label, question["options"], index=None, key=widget_key, disabled=submitted
                )
            else:
                answers[question["id"]] = st.text_input(
                    label, key=widget_key, disabled=submitted, max_chars=80
                )
        check = st.form_submit_button("Check answers", type="primary", disabled=submitted)
    if check:
        if any(answer is None or not str(answer).strip() for answer in answers.values()):
            st.warning("Answer every question before checking.")
        else:
            results = []
            for question in questions:
                answer = answers[question["id"]]
                correct = answer_matches(answer, question)
                repository.record_attempt(
                    question,
                    answer,
                    correct,
                    attempt_id=f"{st.session_state[token_key]}:{question['id']}",
                )
                results.append({"question": question, "answer": answer, "correct": correct})
            st.session_state[result_key] = results
            st.rerun()
    if result_key in st.session_state:
        results = st.session_state[result_key]
        st.success(
            f"Result: {sum(result['correct'] for result in results)}/{len(results)} correct. Your progress has been saved."
        )
        for result in results:
            question = result["question"]
            with st.expander(
                f"{'✅' if result['correct'] else '🔎'} {question['prompt']}",
                expanded=not result["correct"],
            ):
                st.write(f"Your answer: {result['answer']}")
                st.write(f"Answer: {question['answer']}")
                st.write(question["explanation"])
        if st.button("Try again", key=key + "_retry"):
            del st.session_state[result_key]
            del st.session_state[token_key]
            st.rerun()


def api_key() -> str | None:
    """Read configured secrets without displaying or persisting them."""
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return None
