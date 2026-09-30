import streamlit as st

from components.common import get_repository, heading, quiz
from data.content import get_question, load_reading


def render():
    repository = get_repository()
    heading("My Mistakes", "Use explanations and targeted retries to turn mistakes into progress.")
    include_resolved = st.checkbox("Include resolved mistakes")
    mistakes = repository.get_mistakes(include_resolved)
    if not mistakes:
        st.info("No mistakes to review yet. Wrong answers appear here automatically.")
        return
    topics = sorted({f"{m['skill']} · {m['topic']}" for m in mistakes})
    topic = st.selectbox("Filter by topic", ["All topics", *topics])
    for mistake in mistakes:
        if topic != "All topics" and f"{mistake['skill']} · {mistake['topic']}" != topic:
            continue
        with st.container(border=True):
            st.markdown(
                f"**{'✅' if mistake['resolved'] else '🔎'} {mistake['skill']} · {mistake['topic']} · {mistake['prompt']}**"
            )
            st.caption(
                f"Incorrect attempts: {mistake['wrong_count']} · last seen {mistake['last_seen'][:10]}"
            )
            question = get_question(mistake["question_id"])
            if question:
                if question["skill"] == "Reading":
                    for practice in load_reading():
                        if any(q["id"] == question["id"] for q in practice["questions"]):
                            st.markdown(practice["passage"])
                            break
                quiz([question], "mistake_" + question["id"], repository)
                with st.expander("Review the previous answer and explanation"):
                    st.write(f"Previous answer: {mistake['user_answer']}")
                    st.write(f"Correct answer: {mistake['answer']}")
                    st.write(mistake["explanation"])
            else:
                st.write(f"Previous answer: {mistake['user_answer']}")
                st.write(f"Correct answer: {mistake['answer']}")
                st.write(mistake["explanation"])
                if mistake["skill"] == "Vocabulary":
                    st.caption("Open Vocabulary to review this card when it is due.")
            if not mistake["resolved"] and st.button(
                "Mark as reviewed", key="resolve_" + mistake["question_id"]
            ):
                repository.resolve_mistake(mistake["question_id"])
                st.rerun()
