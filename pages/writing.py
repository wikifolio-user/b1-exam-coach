from uuid import uuid4

import streamlit as st

from components.common import api_key, get_repository, heading
from data.content import load_writing
from services.ai_service import evaluate_writing


def show_feedback(feedback: dict):
    st.caption(f"Feedback provider: {feedback['provider']} · {feedback['word_count']} words")
    st.warning(feedback["disclaimer"])
    if feedback.get("fallback_reason"):
        st.info(feedback["fallback_reason"])
    for column, (criterion, score) in zip(st.columns(4), feedback["scores"].items()):
        column.metric(criterion, f"{score}/5")
    st.write(f"**Training estimate: {feedback['total']}/20**")
    for title, field in [
        ("What works", "strengths"),
        ("Try next", "improvements"),
        ("Task points to check", "missing_points"),
        ("Useful phrases", "useful_phrases"),
    ]:
        if feedback.get(field):
            st.subheader(title)
            for item in feedback[field]:
                st.write(f"• {item}")
    st.info(feedback["exam_tip"])
    if feedback.get("improved_version"):
        with st.expander("Example revision"):
            st.write(feedback["improved_version"])


def render():
    repository = get_repository()
    profile = repository.get_settings()
    heading(
        "Writing Trainer",
        "Email, Article and Story · aim for about 100 words and cover every task point.",
    )
    kind = st.selectbox("Text type", ["Email", "Article", "Story"])
    tasks = [task for task in load_writing() if task["kind"] == kind]
    task = st.selectbox("Writing task", tasks, format_func=lambda item: item["title"])
    with st.container(border=True):
        st.write(task["prompt"])
        for point in task["points"]:
            st.write(f"• {point}")
        if task.get("starter"):
            st.info(f"Start your story with: {task['starter']}")
    key = "writing_" + task["id"]
    configured_key = api_key()
    with st.form(key + "_form"):
        text = st.text_area(
            "Your draft",
            height=270,
            max_chars=12000,
            key=key + "_draft",
            placeholder="Write your English text here…",
        )
        request_ai = st.checkbox(
            "Send this task and draft to OpenAI for AI feedback",
            value=False,
            disabled=not (profile["ai_enabled"] and configured_key),
            key=key + "_ai",
        )
        st.caption(
            "Offline feedback checks length, structure and language clues. AI feedback sends your draft to OpenAI only when selected above."
        )
        submitted = st.form_submit_button("Get feedback and save", type="primary")
    if submitted:
        if not text.strip():
            st.warning("Write a draft before requesting feedback.")
        else:
            with st.spinner("Checking your writing…"):
                feedback = evaluate_writing(
                    text,
                    task,
                    use_ai=bool(request_ai and profile["ai_enabled"] and configured_key),
                    api_key=configured_key,
                    model=profile["openai_model"],
                )
                repository.save_writing(task["id"], kind, text, feedback, submission_id=uuid4().hex)
            st.session_state[key + "_feedback"] = feedback
            st.success("Your draft and feedback have been saved.")
    if key + "_feedback" in st.session_state:
        show_feedback(st.session_state[key + "_feedback"])
    history = [item for item in repository.get_writing() if item["task_id"] == task["id"]]
    if history:
        with st.expander(f"Saved drafts for this task ({len(history)})"):
            for item in reversed(history[-10:]):
                st.markdown(
                    f"**{item['created_at'][:16]} · {item['feedback']['total']}/20 · {item['feedback']['provider']}**"
                )
                st.write(item["text"])
