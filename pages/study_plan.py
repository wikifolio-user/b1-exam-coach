import streamlit as st

from components.common import get_repository, heading
from data.content import load_vocabulary
from services.adaptive_service import build_study_plan, topic_stats


def render():
    repository = get_repository()
    settings = repository.get_settings()
    attempts = repository.get_attempts()
    due = len(repository.due_cards(load_vocabulary()))
    heading("Study Plan", f"Your {settings['daily_minutes']}-minute plan adapts as you practise.")
    for index, step in enumerate(
        build_study_plan(attempts, settings, due, len(repository.get_writing())), 1
    ):
        with st.container(border=True):
            st.subheader(f"{index}. {step['title']}")
            st.write(f"**{step['minutes']} minutes · {step['skill']}**")
            st.write(step["reason"])
            if step.get("topic"):
                st.caption(f"Focus topic: {step['topic']}")
    st.info(
        "Open the matching page in the sidebar. The plan recalculates from saved answers and vocabulary due dates."
    )
    with st.expander("How your plan is chosen"):
        st.write(
            "Topics with lower mastery receive priority. Small samples are treated cautiously. Unpractised skills need an initial check; due vocabulary and writing practice are included in the daily budget."
        )
        stats = topic_stats(attempts)
        if stats:
            st.dataframe(stats, hide_index=True, use_container_width=True)
