import streamlit as st

from components.common import get_repository, heading, quiz
from data.content import load_grammar
from services.adaptive_service import choose_question


def render():
    repository = get_repository()
    heading(
        "Grammar Trainer", "Practise a topic or let your recent answers choose the next question."
    )
    questions = load_grammar()
    topic = st.selectbox("Focus", ["Adaptive practice", *sorted({q["topic"] for q in questions})])
    selected_topic = None if topic == "Adaptive practice" else topic
    key = "grammar_current_" + topic
    if key not in st.session_state:
        st.session_state[key] = choose_question(
            questions, repository.get_attempts(), selected_topic
        )
    question = st.session_state[key]
    if question is None:
        st.info("No questions for this topic yet.")
        return
    st.caption(f"Topic: {question['topic']}")
    quiz([question], f"grammar_{question['id']}", repository)
    if st.button("Next question"):
        for suffix in ("_results", "_token"):
            st.session_state.pop(f"grammar_{question['id']}" + suffix, None)
        st.session_state[key] = choose_question(
            [q for q in questions if q["id"] != question["id"]] or questions,
            repository.get_attempts(),
            selected_topic,
        )
        st.rerun()
