"""Streamlit entry point: streamlit run app.py."""

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

from components.common import get_repository  # noqa: E402
from pages import dashboard, grammar, mistakes, progress, reading  # noqa: E402
from pages import settings, study_plan, vocabulary, writing  # noqa: E402

st.set_page_config(page_title="B1 Exam Coach – Phase 2", page_icon="🎯", layout="wide")
profile = get_repository().get_settings()
with st.sidebar:
    st.title("🎯 B1 Exam Coach")
    st.caption("PHASE 2 · Cambridge B1 Preliminary")
    st.write(f"Welcome, {profile['learner_name']}!")
    st.caption(f"Daily goal: {profile['daily_minutes']} minutes")

navigation = st.navigation(
    {
        "Your learning": [
            st.Page(
                dashboard.render, title="Dashboard", icon="🏠", default=True, url_path="dashboard"
            ),
            st.Page(study_plan.render, title="Study Plan", icon="🎯", url_path="study-plan"),
        ],
        "Practice": [
            st.Page(reading.render, title="Reading", icon="📖", url_path="reading"),
            st.Page(grammar.render, title="Grammar", icon="🧠", url_path="grammar"),
            st.Page(vocabulary.render, title="Vocabulary", icon="📚", url_path="vocabulary"),
            st.Page(writing.render, title="Writing", icon="✍️", url_path="writing"),
            st.Page(mistakes.render, title="My Mistakes", icon="🔎", url_path="mistakes"),
        ],
        "Your profile": [
            st.Page(progress.render, title="Progress", icon="📊", url_path="progress"),
            st.Page(settings.render, title="Settings", icon="⚙️", url_path="settings"),
        ],
    }
)
with st.sidebar:
    st.divider()
    st.caption(
        "Original practice material. Writing estimates are for training; they are not official Cambridge scores."
    )
navigation.run()
