from datetime import date

import streamlit as st

from components.common import get_repository, heading
from data.content import load_vocabulary
from services.adaptive_service import build_study_plan, topic_stats
from services.progress_service import learning_summary


def render():
    repository = get_repository()
    profile = repository.get_settings()
    attempts, writing = repository.get_attempts(), repository.get_writing()
    summary = learning_summary(attempts, writing)
    due = len(repository.due_cards(load_vocabulary()))
    heading(
        "Your next step towards B1",
        f"Welcome, {profile['learner_name']}. Small, regular practice builds confidence.",
    )
    cols = st.columns(4)
    cols[0].metric("Practice answers", summary["attempts"])
    cols[1].metric(
        "Accuracy", f"{summary['accuracy']:.0%}" if summary["accuracy"] is not None else "—"
    )
    cols[2].metric("Study streak", f"{summary['streak']} days")
    cols[3].metric("Words due", due)
    st.subheader("Today's mission")
    for step in build_study_plan(attempts, profile, due, len(writing)):
        with st.container(border=True):
            st.markdown(f"**{step['title']} · {step['minutes']} min**")
            st.write(step["reason"])
    left, right = st.columns(2)
    with left:
        st.subheader("Focus areas")
        stats = sorted(topic_stats(attempts), key=lambda row: row["weakness"], reverse=True)[:3]
        if not stats:
            st.info("Start with Reading and Grammar to discover which topics need practice.")
        for row in stats:
            st.write(
                f"**{row['skill']} · {row['topic']}** — {row['correct']}/{row['attempts']} correct"
            )
            st.progress(float(row["mastery"]), text="Estimated mastery")
    with right:
        st.subheader("Keep going")
        st.write(
            f"You have completed **{len(writing)} writing tasks** and **{summary['today_count']} practice activities today**."
        )
        st.write(
            "Use My Mistakes to revisit explanations. Try an email, article or story of about 100 words in Writing."
        )
        if profile["exam_date"]:
            days = (date.fromisoformat(profile["exam_date"]) - date.today()).days
            st.info(f"Exam date: {profile['exam_date']} · {days} days from today")
    st.caption(
        "This phase trains Reading and Writing, grammar and vocabulary. Listening and Speaking are outside Phase 2."
    )
